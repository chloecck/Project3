ctx = {
  restore() {
    console.clear();
    console.info("ctx restore start...");
    for (const [k, v] of Object.entries(this)) {
      if (typeof v !== "function") {
        const toRestore = u.colVar(k);
        if (toRestore !== undefined) {
          try {
            this[k] = JSON.parse(toRestore);
            console.info(`${k}: ${toRestore} restored JSON`);
          } catch (e) {
            this[k] = toRestore;
            console.info(`${k}: ${toRestore} restored`);
          }
        }
      }
    }
    console.info("ctx restore end---");
  },
  save() {
    this.userPrev(this.user());
    this.user(null);
    this.postPrev(this.post());
    this.post(null);
    console.info("ctx save start...");
    for (const [k, v] of Object.entries(this)) {
      if (typeof v !== "function") {
        if (k.includes("pm")) {
          console.info("_pm skipped");
        } else if (typeof v === "object") {
          u.colVar(k, JSON.stringify(v));
          console.info(`${k}: ${JSON.stringify(v, null, 2)} saved`);
        } else {
          u.colVar(k, v);
          console.info(`${k}:${v} saved`);
        }
      }
    }
    console.info("ctx save end---");
  },
  updateUser(...keys) {
    this.user(u.update(this.userPrev(), this.user(), ...keys));
  },
  skip() {
    this.save();
    u.skip();
  },
  _pm: pm,
  pm(pm) {
    if (pm !== undefined) this._pm = pm;
    return this._pm;
  },
  _encodeJSON: false,
  _decodeJSON: false,
  encodeJSON(flag) {
    if (typeof flag === "boolean") this._encodeJSON = flag;
    return this._encodeJSON;
  },
  decodeJSON(flag) {
    if (typeof flag === "boolean") this._decodeJSON = flag;
    return this._decodeJSON;
  },
  _user: null,
  _userPrev: null,
  _userNo: -1,
  _userVarName: "user",
  _userRepo: {},
  userVarName(username) {
    if (username !== undefined) this._userVarName = username;
    if (username in this)
      console.warn(
        `'{username}' has defined in ctx. It may overwrite when restoring ctx`
      );
    return this._userVarName;
  },
  user(user) {
    if (user !== undefined) this._user = user;
    return this._user;
  },
  userPrev(userPrev) {
    if (userPrev !== undefined) this._userPrev = userPrev;
    return this._userPrev;
  },
  userRepo(userVarName, user) {
    if (userVarName === undefined) return this._userRepo;
    if (user !== undefined) {
      this._userRepo[userVarName] = user;
    }
    return this._userRepo[userVarName];
  },
  userNo(num) {
    if (Number.isInteger(num)) this._userNo = Math.max(num, 0);
    return this._userNo;
  },
  nextUser() {
    this.userPrev(this.user());
    this.user(null);
    this.userNo(Math.max(this.userNo(), 0) + 1);
    this.userVarName(`${this.userVarName()}${this.userNo()}`);
  },
  saveUserToEnv(
    userVarName,
    { encode = this.encodeJSON(), prev = false } = {}
  ) {
    if (userVarName === undefined) userVarName = this.userVarName();
    const user = prev === true ? this.userPrev() : this.user();
    if (encode) {
      u.envVar(userVarName, u.jsonEncode(user));
    } else {
      u.envVar(userVarName, JSON.stringify(user));
    }
  },
  loadUserFromEnv(userVarName, { decode = this.decodeJSON(), rename } = {}) {
    if (userVarName === undefined) userVarName = this.userVarName();

    const json = u.envVar(userVarName);

    let user;
    if (decode) {
      user = u.jsonDecode(json);
    } else {
      user = JSON.parse(json);
    }

    this.userRepo(rename ?? userVarName, user);
    return user;
  },
  spreadUserToEnv(userVarName, { prev = true } = {}) {
    if (userVarName === undefined) userVarName = this.userVarName();
    const user = prev === true ? this.userPrev() : this.user();
    u.spreadToEnv(user, userVarName);
  },
  _post: null,
  _postPrev: null,
  _postNo: -1,
  _postVarName: "post",
  _postRepo: {},
  postVarName(postname) {
    if (postname !== undefined) this._postVarName = postname;
    if (postname in this)
      console.warn(
        `'{postname}' has defined in ctx. It may overwrite when restoring ctx`
      );
    return this._postVarName;
  },
  post(post) {
    if (post !== undefined) this._post = post;
    return this._post;
  },
  postPrev(postPrev) {
    if (postPrev !== undefined) this._postPrev = postPrev;
    return this._postPrev;
  },
  postRepo(postVarName, post) {
    if (postVarName === undefined) return this._postRepo;
    if (post !== undefined) {
      this._postRepo[postVarName] = post;
    }
    return this._postRepo[postVarName];
  },
  savePostToEnv(
    postVarName,
    { encode = this.encodeJSON(), prev = false } = {}
  ) {
    if (postVarName === undefined) postVarName = this.postVarName();
    const post = prev === true ? this.postPrev() : this.post();
    if (encode) {
      u.envVar(postVarName, u.jsonEncode(post));
    } else {
      u.envVar(postVarName, JSON.stringify(post));
    }
  },
  loadPostFromEnv(postVarName, { decode = this.decodeJSON(), rename } = {}) {
    if (postVarName === undefined) postVarName = this.postVarName();

    const json = u.envVar(postVarName);

    let post;
    if (decode) {
      post = u.jsonDecode(json);
    } else {
      post = JSON.parse(json);
    }

    this.postRepo(rename ?? postVarName, post);
    return post;
  },
};

sch = schema = {
  _userSchema: {
    user_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
    user_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
    username: ctx.pm().variables.replaceIn("{{$randomUserName}}"),
    user_bio: ctx.pm().variables.replaceIn("{{$randomPhrase}}"),
  },
  _postSchema: {
    post_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
    post_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
    timestamp: ctx.pm().variables.replaceIn("{{$isoTimestamp}}"),
    msg: ctx.pm().variables.replaceIn("{{$randomLoremSentences}}"),
    user_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
    user_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
    username: ctx.pm().variables.replaceIn("{{$randomUserName}}"),
    user_bio: ctx.pm().variables.replaceIn("{{$randomPhrase}}"),
    reply_to: ctx.pm().variables.replaceIn("{{$randomInt}}"),
    replies: [ctx.pm().variables.replaceIn("{{$randomInt}}")],
  },
  userSchema() {
    return JSON.parse(JSON.stringify(this._userSchema), (k, v) =>
      k === "" ? v : null
    );
  },
  postSchema() {
    return JSON.parse(JSON.stringify(this._postSchema), (k, v) =>
      k === "" ? v : null
    );
  },
  randomUser() {
    return {
      user_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
      user_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
      username: ctx.pm().variables.replaceIn("{{$randomUserName}}"),
      user_bio: ctx.pm().variables.replaceIn("{{$randomFullName}}"),
    };
  },
  randomPost() {
    return {
      post_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
      post_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
      timestamp: ctx.pm().variables.replaceIn("{{$isoTimestamp}}"),
      msg: ctx.pm().variables.replaceIn("{{$randomLoremSentences}}"),
      user_id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
      user_key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
      username: ctx.pm().variables.replaceIn("{{$randomUserName}}"),
      user_bio: ctx.pm().variables.replaceIn("{{$randomPhrase}}"),
      reply_to: ctx.pm().variables.replaceIn("{{$randomInt}}"),
      replies: [ctx.pm().variables.replaceIn("{{$randomInt}}")],
    };
  },
  populateSchema(schema, data) {
    const filtered = Object.fromEntries(
      Object.entries(data).filter(([k, v]) => k in schema)
    );
    return { ...schema, ...filtered };
  },
  user(data) {
    return this.populateSchema(this.userSchema(), data);
  },
  post(data) {
    return this.populateSchema(this.postSchema(), data);
  },
};

req = {
  _protocol: "http",
  _host: ["127", "0", "0", "1"],
  _port: "5000",
  protocol(p) {
    if (typeof p === "string") this._protocol = p;
    return this._protocol;
  },
  host(h) {
    if (Array.isArray(h)) this._host = h;
    return this._host;
  },
  port(p) {
    if (typeof p === "string") this._port = p;
    return this._port;
  },
  baseUrl() {
    return `${this.protocol()}://${this.host().join(".")}:${this.port()}`;
  },
  url(config) {
    const pm = ctx.pm();
    const reqUrl = pm.request.url;

    if (
      config === undefined ||
      Array.isArray(config) ||
      typeof config !== "object"
    ) {
      return reqUrl;
    }

    const props = {
      host: v.isStrArr,
      path: v.isStrArr,
      port: v.isStr,
      protocol: v.isStr,
      query: v.isObjArr,
    };
    config = u.cleanCollect(config, ...Object.keys(props));
    for (const p in config) {
      const [res, msg] = props[p](config[p], p, {
        cast: true,
        trim: true,
        clean: true,
      });
      if (msg) {
        return console.error(msg);
      }
      config[p] = res;
    }
    pm.request.url.update(config);
  },
  json(body) {
    const pm = ctx.pm();

    if (body !== undefined) {
      const mode = "raw";
      const raw = JSON.stringify(body ?? "");
      const op1 = { mode, raw };
      const options = {
        ...op1,
        options: { ...op1, options: { raw: { language: "json" } } },
      };
      pm.request.body.update(options);
      pm.request.upsertHeader({
        key: "Content-Type",
        value: "application/json",
      });
    }

    let reqJSON;
    try {
      reqJSON = JSON.parse(pm.request.body.raw);
    } catch (e) {
      console.warn(`could not parse req body json: ${e}`);
    }

    return reqJSON;
  },
  readUserMetadata(user_id, username) {
    const user = ctx.userPrev();
    if (user_id === undefined) user_id = user?.user_id;
    if (username === undefined) username = user?.username;
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["user"],
      query: [
        { key: "user_id", value: user_id },
        { key: "username", value: username },
      ],
    });
  },
  editUserMetadata(user_id, user_key) {
    const user = ctx.userPrev();
    if (user_id === undefined) user_id = user?.user_id;
    if (user_key === undefined) user_key = user?.user_key;
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["user", user_id, "edit", user_key],
    });
  },
  readPost(post_id) {
    const post = ctx.postPrev();
    console.log(post);
    console.log("post");
    if (post_id === undefined) post_id = post?.post_id;
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["post", post_id],
    });
  },
  deletePost(post_id, key) {
    const post = ctx.postPrev();
    if (post_id === undefined) post_id = post?.post_id;
    if (key === undefined) key = post?.post_key;
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["post", post_id, "delete", key],
    });
  },
  rangePost({ start, end, user_id, username } = {}) {
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["post"],
      query: [
        { key: "start", value: start },
        { key: "end", value: end },
        { key: "user_id", value: user_id },
        { key: "username", value: username },
      ],
    });
  },
};

res = {
  json() {
    let resJSON;
    try {
      resJSON = ctx.pm().response.json();
    } catch (e) {
      console.warn(`could not parse res body json: ${e}`);
    }
    return resJSON;
  },
};

u = utils = {
  skip() {
    ctx.pm().execution.skipRequest();
  },
  envVar(k, v) {
    const pm = ctx.pm();
    if (v !== undefined) {
      pm.environment.set(k, v);
    }
    return pm.environment.get(k);
  },
  colVar(k, v) {
    const pm = ctx.pm();
    if (v !== undefined) {
      pm.collectionVariables.set(k, v);
    }
    return pm.collectionVariables.get(k);
  },
  globalVar(k, v) {
    const pm = ctx.pm();
    if (v !== undefined) {
      pm.globals.set(k, v);
    }
    return pm.globals.get(k);
  },
  spreadToEnv(o, rootName = "root", { encode = false, decode = false } = {}) {
    for (const [k, v] of Object.entries(o)) {
      const keyName = `${rootName}_${k}`;
      if (encode ^ decode) {
        if (encode) this.envVar(keyName, encodeURIComponent(v));
        if (decode) this.envVar(keyName, decodeURIComponent(v));
      } else {
        this.envVar(keyName, v);
      }
    }
  },
  spreadToCol(o, rootName = "root", { encode = false, decode = false } = {}) {
    for (const [k, v] of Object.entries(o)) {
      const keyName = `${rootName}_${k}`;
      if (encode ^ decode) {
        if (encode) this.colVar(keyName, encodeURIComponent(v));
        if (decode) this.colVar(keyName, decodeURIComponent(v));
      } else {
        this.colVar(keyName, v);
      }
    }
  },
  spreadToGlobal(
    o,
    rootName = "root",
    { encode = false, decode = false } = {}
  ) {
    for (const [k, v] of Object.entries(o)) {
      const keyName = `${rootName}_${k}`;
      if (encode ^ decode) {
        if (encode) this.globalVar(keyName, encodeURIComponent(v));
        if (decode) this.globalVar(keyName, decodeURIComponent(v));
      } else {
        this.globalVar(keyName, v);
      }
    }
  },
  jsonEncode(o) {
    return JSON.stringify(o, (k, v) => {
      if (typeof v === "string") return encodeURIComponent(v);
      return v;
    });
  },
  jsonDecode(j) {
    return JSON.parse(j, (k, v) => {
      if (typeof v === "string") return decodeURIComponent(v);
      return v;
    });
  },
  cleanCollect(o, ...keys) {
    return Object.entries(o).reduce((acc, [k, v]) => {
      if (v !== undefined || v !== null || !keys.includes(k)) {
        acc[k] = v;
      }
      return acc;
    }, {});
  },
  def(varName) {
    return ctx.pm().variables.replaceIn("{{" + varName + "}}");
  },
  update(to, src, ...keys) {
    const filtered = Object.fromEntries(
      Object.entries(src).filter(([k, v]) => keys.includes(k))
    );
    return { ...to, ...filtered };
  },
  tsDiff({ year, month, day, hour, minute, second } = {}) {
    const cur = new Date();
    const t = new Date();
    t.setFullYear(cur.getFullYear() - (year ?? 0));
    t.setMonth(cur.getMonth() - (month ?? 0));
    t.setDate(cur.getDate() - (day ?? 0));
    t.setHours(cur.getHours() - (hour ?? 0));
    t.setMinutes(cur.getHours() - (minute ?? 0));
    t.setSeconds(cur.getSeconds() - (second ?? 0));

    return t.toISOString();
  },
};
u.spread = u.spreadToEnv;

v = validator = {
  isStr(s, sName, { cast = false, trim = false } = {}) {
    if (cast === true) {
      s = `${s}`;
    }
    if (typeof s !== "string") return [s, `${s}: ${sName} should be a string`];
    if (trim === true) {
      s = s.trim();
    }
    return [s, null];
  },
  isStrArr(arr, arrName, { cast = false, trim = false } = {}) {
    if (!Array.isArray(arr)) {
      return [arr, `${arr}: ${arrName} should be an array`];
    }
    if (cast) {
      arr = arr.map((e) => `${e}`);
    }
    if (arr.some((e) => typeof e !== "string"))
      return [arr, `${arr}: ${arrName} should be a string array`];
    if (trim) {
      arr = arr.map((e) => e.trim());
    }
    return [arr, null];
  },
  isObjArr(arr, arrName, { cast = false, trim = false, clean = false } = {}) {
    if (
      !Array.isArray(arr) ||
      arr.some((e) => typeof e !== "object" || Array.isArray(e))
    )
      return [arr, `${arr}: ${arrName} should be an object array`];

    if (clean === true) {
      arr = arr.filter((o) => {
        for (const v of Object.values(o)) {
          if ([undefined, null].includes(v)) {
            return false;
          }
        }
        return true;
      });
    }
    if (cast === true) {
      for (const o of arr) {
        for (const k in o) {
          o[k] = `${o[k]}`;
        }
      }
    }
    if (trim === true) {
      for (const o of arr) {
        for (const k in o) {
          if (typeof o[k] === "string") {
            o[k] = o[k].trim();
          }
        }
      }
    }

    return [arr, null];
  },
  sts(code) {
    const pm = ctx.pm();
    if (Array.isArray(code) && code.every((c) => typeof c === "number")) {
      return pm.expect(pm.response.code).to.be.oneOf(code);
    }
    return ctx.pm().response.to.have.status(code);
  },
  hasJSONBody(k) {
    ctx.pm().response.to.have.jsonBody(k);
  },
  return(...keys) {
    const pm = ctx.pm();
    const keysQuoted = keys.map((k) => `'${k}'`);
    pm.test(`return ${keysQuoted.join(", ")}`, () => {
      v.sts(200);
      for (const k of keys) {
        this.hasJSONBody(k);
      }
    });
  },
  basicErr(msg, code, ...errors) {
    ctx.pm().test(msg, () => {
      this.sts(code);
      this.hasJSONBody("err");
      for (const e of errors) {
        this.hasJSONBody(e);
      }
    });
  },
  eq(e, t) {
    ctx.pm().expect(e).to.equal(t);
  },
  eql(e, t) {
    ctx.pm().expect(e).to.eql(t);
  },
  true(e) {
    ctx.pm().expect(e).to.be.true;
  },
  false(e) {
    ctx.pm().expect(e).to.be.false;
  },
  negate(value, what) {
    return pm.test(
      `'${what}' is expected to be absent or present with trivial value`,
      () => {
        this.true(
          [undefined, null, ""].includes(value) ||
            Object.keys(value).length === 0
        );
      }
    );
  },
  user_id(user_id, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(user_id, "user_id");
    }
    pm.test("'user_id' should be a postive int", () => {
      pm.expect(Number.isInteger(user_id)).to.be.true;
      pm.expect(user_id > 0).to.be.true;
    });
  },
  user_key(user_key, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(user_key, "user_key");
    }
    pm.test("'user_key' should be a non-empty string", () => {
      pm.expect(typeof user_key === "string").to.be.true;
      pm.expect(!user_key.trim()).to.be.false;
    });
  },
  username(username, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(username, "username");
    }
    pm.test("'username' should be a non-empty string", () => {
      pm.expect(typeof username === "string").to.be.true;
      pm.expect(!username.trim()).to.be.false;
    });
  },
  user_bio(user_bio, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(user_bio, "user_bio");
    }
    pm.test("'user_bio' should be a non-empty string", () => {
      pm.expect(typeof user_bio === "string").to.be.true;
      pm.expect(!user_bio.trim()).to.be.false;
    });
  },
  ts(timestamp, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(timestamp, "timestamp");
    }

    pm.test("'timestamp' is ISO format", () => {
      const isoRegex =
        /^(?:\d{4}-[01]\d-[0-3]\d[T ][0-2]\d:[0-5]\d:[0-5]\d(\.\d{3}|\.\d{6})?)(?:[Zz]|([+\-][0-2]\d:[0-5]\d))?$/;
      pm.expect(isoRegex.test(timestamp)).to.be.true;
    });
    pm.test("'timestamp' has correct date and time", () => {
      const timeDiff = Math.abs(new Date(timestamp) - new Date());
      pm.expect(timeDiff).to.be.lessThan(3e3);
    });
  },
  users(cur, prev, ...keys) {
    const pm = ctx.pm();
    if (cur === undefined) cur = ctx.user();
    if (prev === undefined) prev = ctx.userPrev();
    if (keys.length === 0) keys = Object.keys(cur);
    const keysQuoted = keys.map((k) => `'${k}'`);
    pm.test(`return correct ${keysQuoted.join(", ")}`, () => {
      for (const k of keys) {
        v.eq(cur[k], prev[k]);
      }
    });
  },
  post_id(post_id, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(post_id, "post_id");
    }
    pm.test("'post_id' should be a postive int", () => {
      pm.expect(Number.isInteger(post_id)).to.be.true;
      pm.expect(post_id > 0).to.be.true;
    });
  },
  post_key(post_key, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(post_key, "post_key");
    }
    pm.test("'post_key' should be a non-empty string", () => {
      pm.expect(typeof post_key === "string").to.be.true;
      pm.expect(!post_key.trim()).to.be.false;
    });
  },
  msg(msg, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(msg, "msg");
    }
    pm.test("'msg' should be a non-empty string", () => {
      pm.expect(typeof msg === "string").to.be.true;
      pm.expect(!msg.trim()).to.be.false;
    });
  },
  reply_to(reply_to, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(reply_to, "reply_to");
    }
    pm.test("'reply_to' should be a postive int", () => {
      pm.expect(Number.isInteger(reply_to)).to.be.true;
      pm.expect(reply_to > 0).to.be.true;
    });
  },
  replies(replies, negate = false) {
    const pm = ctx.pm();
    if (negate === true) {
      return this.negate(replies, "replies");
    }

    pm.test("'replies' should be a list", () => {
      this.true(Array.isArray(replies));
    });
    pm.test("'replies' should be a list of ints", () => {
      this.true(replies.every((e) => Number.isInteger(e)));
    });
    pm.test("'replies' should be a list of postive ints", () => {
      this.true(replies.every((e) => e > 0));
    });
  },
  posts(cur, prev, ...keys) {
    const pm = ctx.pm();
    if (cur === undefined) cur = ctx.post();
    if (prev === undefined) prev = ctx.postPrev();
    if (keys.length === 0) keys = Object.keys(cur);
    const keysQuoted = keys.map((k) => `'${k}'`);
    pm.test(`return correct ${keysQuoted.join(", ")}`, () => {
      for (const k of keys) {
        v.eq(cur[k], prev[k]);
      }
    });
  },
};

ctx.restore();
