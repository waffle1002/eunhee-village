/* window.claude.use() 대신 Firebase(Realtime Database + 익명 로그인)를 쓰는 연결 코드 */
window.VILLAGE_FIREBASE = window.VILLAGE_FIREBASE || {
  apiKey: "", authDomain: "", databaseURL: "", projectId: "", appId: ""
};
window.VILLAGE_OWNER_EMAIL = window.VILLAGE_OWNER_EMAIL || "eunhee100s2@gmail.com";

(function(){
  const cfg = window.VILLAGE_FIREBASE;
  if(!cfg.apiKey || !window.firebase) return;            // 설정 전에는 혼자 노는 모드
  firebase.initializeApp(cfg);
  const auth = firebase.auth(), rtdb = firebase.database();

  const ready = new Promise(res => {
    const off = auth.onAuthStateChanged(u => {
      if(u){ off(); res(u); } else auth.signInAnonymously().catch(() => res(null));
    });
  });

  /* 은희 전용 구글 로그인 (연구소 자물쇠에서 호출) */
  window.villageOwnerLogin = async () => {
    const p = new firebase.auth.GoogleAuthProvider();
    try{ await auth.signInWithPopup(p); location.reload(); }catch(e){ alert('로그인하지 못했어요.'); }
  };
  window.villageLogout = async () => { await auth.signOut(); location.reload(); };

  const isOwnerUser = u => !!(u && !u.isAnonymous && u.email && u.email.toLowerCase() === window.VILLAGE_OWNER_EMAIL.toLowerCase());

  const user = {
    id: async () => (await ready)?.uid || null,
    isOwner: async () => isOwnerUser(await ready),
    can: async () => !!(await ready)
  };

  const snapOf = val => ({ docs: Object.entries(val || {}).map(([id, v]) => ({ id, data: () => v })) });
  const db = {
    collection: name => ({
      onSnapshot(cb, err){
        ready.then(u => {
          if((name === 'secret' || name === 'applies') && !isOwnerUser(u)){   // 비밀 편지: 주인장 말고는 내 것만
            if(!u) return;
            rtdb.ref(name + '/' + u.uid).on('value', s => cb(snapOf(s.val() ? { [u.uid]: s.val() } : {})), e => err && err(e));
            return;
          }
          rtdb.ref(name).on('value', s => cb(snapOf(s.val())), e => err && err(e));
        });
        return () => rtdb.ref(name).off();
      }
    }),
    doc: path => ({
      set: async obj => { await ready; return rtdb.ref(path).set(JSON.parse(JSON.stringify(obj))); },
      delete: async () => { await ready; return rtdb.ref(path).remove(); }
    })
  };

  /* 실시간 접속: presence/<탭 id> 에 위치를 두고, 창을 닫으면 자동 삭제 */
  const tab = Math.random().toString(36).slice(2, 10);
  let mine = {}, myRef = null;
  const room = {
    async presence(p){
      const u = await ready; if(!u) return;
      Object.assign(mine, p);
      if(!myRef){ myRef = rtdb.ref('presence/' + tab); myRef.onDisconnect().remove();
        setInterval(() => myRef.update({ t: firebase.database.ServerValue.TIMESTAMP }).catch(()=>{}), 120000); }
      return myRef.set(Object.assign({}, mine, { by: u.uid, t: firebase.database.ServerValue.TIMESTAMP }));
    },
    onPeers(cb, onClose){
      ready.then(u => {
        if(!u){ onClose && onClose(); return; }
        rtdb.ref('presence').on('value', s => {
          const now = Date.now(), peers = [];
          for(const [id, v] of Object.entries(s.val() || {})){
            if(!v || (v.t && now - v.t > 10*60*1000)) continue;   // 오래된 흔적 무시
            peers.push({ peer: id, isMe: id === tab, kind: 'viewer', by: v.by, presence: v });
          }
          cb({ peers });
        }, () => onClose && onClose());
      });
    }
  };

  const map = { user, db, room };
  window.claude = { use: async n => map[n] || null };
})();
