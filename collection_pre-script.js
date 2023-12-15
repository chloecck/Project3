ctx = {
  restore() {
    console.clear();
    console.info("ctx restoring...");
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
  },
  save() {
    this.userPrev(this.user());
    this.user(null);
    console.info("ctx saving...");
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
  _userVarName: "user",
  _user: null,
  _userNo: -1,
  _userPrev: null,
  userVarName(username) {
    if (username !== undefined) this._userVarName = username;
    if (username in this) console.warn(`'{username}' has defined in ctx. It may overwrite when restoring ctx`);
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
  userNo(num) {
    if (Number.isInteger(num)) this._userNo = num;
    return this._userNo;
  },
  nextUser() {
    this.userPrev(this.user());
    this.user(null);
    this.userNo(Math.max(this.userNo(), 0) + 1);
    this.userVarName(`${this.userVarName()}${this.userNo()}`);
  },
  saveUserToEnv({ encode = this.encodeJSON(), prev = false } = {}) {
    const userVarName = this.userVarName();
    const user = !prev ? this.user() : this.userPrev();
    if (encode) {
      u.envVar(userVarName, u.jsonEncode(user));
    } else {
      u.envVar(userVarName, JSON.stringify(user));
    }
  },
  parseUserFromEnv(decode = this.decodeJSON()) {
    const json = u.getEnvVar(this.userVarName());
    let user;
    if (decode) {
      user = u.jsonDecode(json);
    } else {
      user = JSON.parse(json);
    }
    return user;
  },
  spreadUserToEnv({ prev = true } = {}) {
    const user = prev ? this.userPrev() : this.user();
    console.warn("user", user);
    u.spreadToEnv(user, this.userVarName());
  },
};

sch = schema = {
  _userSchema: {
    id: pm.variables.replaceIn("{{$randomInt}}"),
    key: pm.variables.replaceIn("{{$randomPassword}}"),
    username: pm.variables.replaceIn("{{$randomUserName}}"),
    display_name: pm.variables.replaceIn("{{$randomFullName}}"),
  },
  userSchema() {
    return JSON.parse(JSON.stringify(this._userSchema), (k, v) => (k === "" ? v : null));
  },
  randomUser() {
    return {
      id: ctx.pm().variables.replaceIn("{{$randomInt}}"),
      key: ctx.pm().variables.replaceIn("{{$randomPassword}}"),
      username: ctx.pm().variables.replaceIn("{{$randomUserName}}"),
      display_name: ctx.pm().variables.replaceIn("{{$randomFullName}}"),
    };
  },
  populateSchema(schema, data) {
    const filtered = Object.fromEntries(Object.entries(data).filter(([k, v]) => k in schema));
    return { ...schema, ...filtered };
  },
  user(data) {
    return this.populateSchema(this.userSchema(), data);
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

    if (config === undefined || Array.isArray(config) || typeof config !== "object") {
      return reqUrl;
    }

    const props = { host: v.isStrArr, path: v.isStrArr, port: v.isStr, protocol: v.isStr(), query: v.isObjArr };
    config = u.clean(config, ...Object.keys(props));

    for (const p in config) {
      const [msg, ok] = props[p](config[p], p);
      if (!ok) {
        return console.error(msg);
      }
    }

    pm.request.url.update(config);
  },
  readUserMetadata(id, key) {
    const user = ctx.userPrev();
    if (id === undefined) id = user?.id;
    if (key === undefined) key = user?.key;
    console.warn("setup", {
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["user"],
      query: [{ id }, { key }],
    });
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["user"],
      query: [{ id }, { key }],
    });
  },
  editUserMetadata(id, key) {
    const user = ctx.userPrev();
    if (id === undefined) id = user?.id;
    if (key === undefined) key = user?.key;
    this.url({
      protocol: this.protocol(),
      host: this.host(),
      port: this.port(),
      path: ["user", id, "edit", key],
    });
  },
};

res = {
  json() {
    let resJSON;
    try {
      resJSON = ctx.pm().response.json();
    } catch (e) {
      console.warn(`could not parse body json: ${e}`);
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
  spreadToGlobal(o, rootName = "root", { encode = false, decode = false } = {}) {
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
  clean(o, ...keys) {
    return Object.entries(o).reduce((acc, [k, v]) => {
      console.log(k, v);
      if (v !== undefined || v !== null || !keys.includes(k)) {
        console.log("acc", acc);
        acc[k] = v;
      }
      return acc;
    }, {});
  },
};
u.spread = u.spreadToEnv;

v = validator = {
  checkStr(s, sName) {
    if (typeof s !== "string") return [`${s}: ${sName} should be a string`, false];
    return [s, true];
  },
  isStrArr(arr, arrName) {
    if (!Array.isArray(arr) || arr.some((e) => typeof e !== "string")) return [`${arr}: ${arrName} should be a string array`, false];
    return [arr, true];
  },
  isObjArr(arr, arrName) {
    if (!Array.isArray(arr) || arr.some((e) => typeof e !== "object" || Array.isArray(e))) return [`${arr}: ${arrName} should be an object array`, false];
    return [arr, true];
  },
  sts(code) {
    ctx.pm().response.to.have.status(code);
  },
  hasJSONBody(k) {
    ctx.pm().response.to.have.jsonBody(k);
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
  id(id) {
    const pm = ctx.pm();
    pm.test("'id' should be a postive int", () => {
      pm.expect(Number.isInteger(id)).to.be.true;
      pm.expect(id > 0).to.be.true;
    });
  },
  key(key) {
    const pm = ctx.pm();
    pm.test("'key' should be a non-empty string", () => {
      pm.expect(typeof key === "string").to.be.true;
      pm.expect(!key.trim()).to.be.false;
    });
  },
  username(username) {
    const pm = ctx.pm();
    pm.test("'username' should be a non-empty string", () => {
      pm.expect(typeof username === "string").to.be.true;
      pm.expect(!username.trim()).to.be.false;
    });
  },
  display_name(display_name) {
    const pm = ctx.pm();
    pm.test("'display_name' should be a non-empty string", () => {
      pm.expect(typeof display_name === "string").to.be.true;
      pm.expect(!display_name.trim()).to.be.false;
    });
  },
  ts(timestamp) {
    const pm = ctx.pm();
    pm.test("'timestamp' is ISO format", () => {
      const isoRegex = /^(?:\d{4}-[01]\d-[0-3]\d[T ][0-2]\d:[0-5]\d:[0-5]\d(\.\d{3}|\.\d{6})?)(?:[Zz]|([+\-][0-2]\d:[0-5]\d))?$/;
      pm.expect(isoRegex.test(timestamp)).to.be.true;
    });
    pm.test("'timestamp' has correct date and time", () => {
      const timeDiff = Math.abs(new Date(timestamp) - new Date());
      pm.expect(timeDiff).to.be.lessThan(3e3);
    });
  },
};

ctx.restore();
