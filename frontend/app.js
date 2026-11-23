(() => {
  const CAT_META = {
    gs: {
      color: "#facc15",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" fill-rule="evenodd" aria-hidden="true"><path d="M12 4C8.9 4 6.7 6.1 6.7 8.8c0 1.4.6 2.6 1.5 3.4l.4 2.4c.1.7.7 1.2 1.4 1.2h4c.7 0 1.3-.5 1.4-1.2l.4-2.4c.9-.8 1.5-2 1.5-3.4C17.3 6.1 15.1 4 12 4zm-2.3 5.5a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm4.6 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm-3.6 3.7h2.6v1.2h-2.6v-1.2z"/><path d="M6.4 8.2L3.1 6.3l-.9 1.6 3.6 2.1M6.2 11.1l-3.8.2.1 1.8 3.9-.2M6.8 13.7l-3.2 2.4 1.1 1.5 3.1-2.3M17.6 8.2l3.3-1.9.9 1.6-3.6 2.1M17.8 11.1l3.8.2-.1 1.8-3.9-.2M17.2 13.7l3.2 2.4-1.1 1.5-3.1-2.3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/></svg>`,
    },
    heart: {
      color: "#fb7185",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" fill-rule="evenodd" aria-hidden="true"><path d="M12 20.6l-1.3-1.2C5.4 14.7 2.5 11.9 2.5 8.4 2.5 5.6 4.7 3.5 7.5 3.5c1.7 0 3.3.8 4.5 2.2 1.2-1.4 2.8-2.2 4.5-2.2 2.8 0 5 2.1 5 4.9 0 3.5-2.9 6.3-8.2 11L12 20.6zm-.6-12.1L9.7 12l2.6 1.5-1.1 3.7 1.3.4 1.3-4.6-2.5-1.5 1.5-3.1-1.4.1z"/></svg>`,
    },
    container: {
      color: "#ef4444",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 21.1l-1.4-1.3C5.1 14.9 2 12 2 8.2 2 5.2 4.4 2.9 7.4 2.9c1.8 0 3.5.9 4.6 2.3 1.1-1.4 2.8-2.3 4.6-2.3 3 0 5.4 2.3 5.4 5.3 0 3.8-3.1 6.7-8.6 11.6L12 21.1z" stroke="currentColor" stroke-width="1"/><path d="M7.3 6.4c-.9.3-1.6 1.1-1.7 2.1" stroke="#fff4e6" stroke-width="1.6" stroke-linecap="round" fill="none" opacity="0.7"/></svg>`,
    },
    bean: {
      color: "#4ade80",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.2 12.2c-.3-3.5-2.3-6.5-6.2-7-.5 3.9 2 6.7 5.5 7.3v2.3c-1.8-.3-3.8.5-4.7 2.2-1 1.9-.2 4.2 1.8 4.9 2.4.8 5.2-.6 6.1-3.1.4-1 .4-2.1.2-3.1v-3.5c3-.7 5-3.4 4.7-6.8-3.5.4-5.7 2.8-6.4 6.2l-1 .6z"/></svg>`,
    },
    fairy: {
      color: "#f472b6",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 3l2.2 5.4 5.8.5-4.4 3.8 1.4 5.7-5-3.1-5 3.1 1.4-5.7L4 8.9l5.8-.5L12 3z"/></svg>`,
    },
    bottle: {
      color: "#38bdf8",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" fill-rule="evenodd" aria-hidden="true"><path d="M9.5 2.5h5v2.2h-5V2.5zM9 5.5h6v2.1l2.8 3.2c.5.6.7 1.3.7 2v6.7c0 1.4-1.1 2.5-2.5 2.5H8c-1.4 0-2.5-1.1-2.5-2.5v-6.7c0-.7.3-1.4.7-2L9 7.6V5.5zm-.8 8.2v4.8h7.6v-4.8H8.2z"/></svg>`,
    },
    thought: {
      color: "#c084fc",
      svg: `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 6.8a4.2 4.2 0 1 0 0 8.4 4.2 4.2 0 0 0 0-8.4z"/><path d="M7.6 9.5C5.2 6.2 2.4 5.5 2.2 7.8c-.2 2.1 2.3 3.7 4.9 3.6M16.4 9.5c2.4-3.3 5.2-4 5.4-1.7.2 2.1-2.3 3.7-4.9 3.6M8.2 13.8c-2.2 1.2-3.4 3.3-2.1 4.4 1.2 1 3-.6 3.6-2.5M15.8 13.8c2.2 1.2 3.4 3.3 2.1 4.4-1.2 1-3-.6-3.6-2.5" opacity="0.82"/></svg>`,
    },
  };

  const REQ_EQUIP_MAP = {
    "bombs": (eq) => eq.bombs,
    "boomerang": (eq) => eq.boomerang,
    "slingshot": (eq) => eq.slingshot,
    "bow": (eq) => eq.bow,
    "hookshot": (eq) => eq.hookshot || eq.longshot,
    "longshot": (eq) => eq.longshot,
    "megaton-hammer": (eq) => eq.hammer,
    "iron-boots": (eq) => eq.iron_boots,
    "hover-boots": (eq) => eq.hover_boots,
    "golden-scale": (eq) => eq.gold_scale,
    "silver-scale": (eq) => eq.silver_scale || eq.gold_scale,
    "goron-bracelet": (eq) => eq.goron_bracelet || eq.silver_gauntlets || eq.gold_gauntlets,
    "silver-gauntlets": (eq) => eq.silver_gauntlets || eq.gold_gauntlets,
    "golden-gauntlets": (eq) => eq.gold_gauntlets,
    "lens-of-truth": (eq) => eq.lens,
    "mirror-shield": (eq) => eq.mirror_shield,
    "zora-tunic": (eq) => eq.zora_tunic,
    "dins-fire": (eq) => eq.dins_fire,
    "ocarina": (eq) => eq.ocarina_fairy || eq.ocarina_time,
    "gerudo-card": (eq) => eq.gerudo_token,
  };

  const CHILD_ONLY_PLACES = new Set(["deku", "jabu", "pozo"]);
  const ADULT_ONLY_PLACES = new Set([
    "bosque", "fuego", "agua", "sombra", "hielo", "fortaleza", "desierto", "ganon",
  ]);

  const state = {
    staticMode: false,
    apiBase: "",
    lang: "zh-CN",
    catalog: null,
    serverState: null,
    viewMode: "overworld", // "overworld" | "place"
    overworldEra: "child", // "child" | "adult" | "all"
    activePlaceId: null,
    activeFloorId: null,
    selectedItemId: null,
    activeCategoryFilter: null, // null | catKey
    navTab: "places", // "places" | "items"
    search: "",
    filterStatus: "all", // "all" | "remaining" | "done"
    filterAge: "child", // "all" | "child" | "adult" | "night"
    autoFollowMap: true,
    showLabels: true,
    lastLinkPlaceFloor: null,
    lastLinkOverworldUv: null,
    linkArrowDeg: null,
    lastLinkMapKey: null,
    lastLinkUv: null,
    lastLinkScene: null,
    // Map pan/zoom
    scale: 1,
    minScale: 0.1,
    maxScale: 4,
    tx: 0,
    ty: 0,
    mapBaseW: 6000,
    mapBaseH: 4364,
    dragging: false,
    dragMoved: false,
    dragStartX: 0,
    dragStartY: 0,
    dragStartTx: 0,
    dragStartTy: 0,
    browsePath: "",
    mapLoadToken: 0,
    mobilePane: "map",
    drawerOpen: false,
    pendingMapFit: false,
    hoveredItemId: null,
    quickCardDock: "bottom",
    hoverCardTimer: null,
  };

  const WEB_STORAGE_KEYS = {
    lang: "oot_map_lang_v1",
    overrides: "oot_map_overrides_v1",
    save: "oot_map_save_v1",
  };

  function readLocalJson(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      const parsed = JSON.parse(raw);
      return parsed ?? fallback;
    } catch {
      return fallback;
    }
  }

  function writeLocalJson(key, val) {
    try {
      if (val === null || val === undefined) {
        localStorage.removeItem(key);
      } else {
        localStorage.setItem(key, JSON.stringify(val));
      }
    } catch {
      // ignore storage quota errors
    }
  }

  function applyTf(tf, x, z) {
    if (!tf || tf.mode === "none") return null;
    return [tf.ax * x + tf.az * z + tf.c, tf.bx * x + tf.bz * z + tf.d];
  }

  function resolvePlaceAndFloorClient(scene, pos, isChild, catalog) {
    if (!scene) return [null, null];
    let pid = null;
    if (scene.startsWith("HyruleField")) {
      if (pos && pos.length >= 3) {
        const [x, , z] = pos;
        if (x >= -160 && x <= -20 && z >= 170 && z <= 310) pid = "lonlon";
        else if (x <= -35 && z >= 360) pid = "lago";
        else pid = "llanura";
      } else {
        pid = "llanura";
      }
    } else {
      const sceneMap = {
        IngoRanch_Adult: "lonlon",
        IngoRanch: "lonlon",
        GanonCastle: "castillo",
        GerudoTrainingGround: "gerudo",
      };
      for (const p of catalog.places || []) {
        for (const sc of p.scenes || []) {
          if (!sceneMap[sc]) sceneMap[sc] = p.id;
        }
      }
      pid = sceneMap[scene] || null;
      if (!pid) {
        const base = scene.replace("_Child", "").replace("_Adult_Alternative", "").replace("_Adult", "");
        for (const p of catalog.places || []) {
          if ((p.scenes || []).some((sc) => sc.startsWith(base))) {
            pid = p.id;
            break;
          }
        }
      }
    }
    if (!pid) return [null, null];
    const place = (catalog.places || []).find((p) => p.id === pid);
    if (!place || !place.maps || !place.maps.length) return [pid, null];
    const mapIds = place.maps.map((m) => m.id);
    if (mapIds.includes("nino") && mapIds.includes("adulto")) {
      return [pid, isChild ? "nino" : "adulto"];
    }
    const rooms = place.dungeon_floors || [];
    if (rooms.length && pos && pos.length >= 3) {
      const [px, py, pz] = pos;
      let bestFloor = null;
      let bestDist = 1e18;
      for (const rm of rooms) {
        const [cx, cy, cz] = rm.center;
        const d = (px - cx) ** 2 + (pz - cz) ** 2 + 4.0 * (py - cy) ** 2;
        if (d < bestDist) {
          bestDist = d;
          for (const cand of rm.floors || [rm.floor_id]) {
            if (mapIds.includes(cand)) {
              bestFloor = cand;
              break;
            }
          }
        }
      }
      if (bestFloor) return [pid, bestFloor];
    }
    return [pid, place.startMap || mapIds[0]];
  }

  function projectPlayerPositionsClient(scene, placeId, floorId, pos, catalog) {
    let overworldUv = null;
    const placeUv = {};
    const place = (catalog.places || []).find((p) => p.id === placeId);
    if (place) {
      if (/^(HyruleField|LonLonRanch|LakeHylia|IngoRanch)/.test(scene) && pos && pos.length >= 3) {
        const res = applyTf(catalog.map?.overworld_hyrule_tf, pos[0], pos[2]);
        if (res) {
          overworldUv = {
            x: Math.round(Math.max(0.02, Math.min(0.98, res[0])) * 10000) / 10000,
            y: Math.round(Math.max(0.02, Math.min(0.98, res[1])) * 10000) / 10000,
          };
        }
      }
      if (!overworldUv && place.pin) {
        overworldUv = { x: place.pin.x, y: place.pin.y };
      }
      if (pos && pos.length >= 3 && place.maps) {
        for (const m of place.maps) {
          const sxy = applyTf(m.transform || place.transform, pos[0], pos[2]);
          if (sxy) {
            const [vx, vy, vw, vh] = m.viewBox || [0, 0, 1000, 1000];
            if (vw > 0 && vh > 0) {
              placeUv[m.id] = {
                x: Math.round(Math.max(-0.08, Math.min(1.08, (sxy[0] - vx) / vw)) * 10000) / 10000,
                y: Math.round(Math.max(-0.08, Math.min(1.08, (sxy[1] - vy) / vh)) * 10000) / 10000,
              };
            }
          }
        }
      }
    }
    return {
      overworld: overworldUv,
      place: placeUv,
      active_place_uv: floorId ? (placeUv[floorId] || null) : null,
    };
  }

  function parseProgressSavBuffer(arrayBuffer, catalog, fileName = "progress.sav", lastModifiedMs = Date.now()) {
    if (arrayBuffer.byteLength < 0x30) throw new Error("Save file too short");
    const dv = new DataView(arrayBuffer);
    const bytes = new Uint8Array(arrayBuffer);
    const magic = dv.getUint32(0, true);
    if (magic !== 0x01020304) throw new Error(`Invalid progress.sav magic: 0x${magic.toString(16)}`);
    const endOff = dv.getUint32(8, true);
    if (endOff < 0x28 || endOff > arrayBuffer.byteLength) throw new Error("Invalid save header");

    const kv = new Map();
    for (let off = 0x28; off + 8 <= endOff; off += 8) {
      kv.set(dv.getUint32(off, true), dv.getUint32(off + 4, true));
    }

    const b64Set = new Set();
    const ptr = kv.get(0xa3db7114) || 0;
    if (ptr >= endOff && ptr < arrayBuffer.byteLength) {
      for (let pos = ptr; pos + 8 <= arrayBuffer.byteLength; pos += 8) {
        const q = dv.getBigUint64(pos, true);
        if (q === 0n) break;
        b64Set.add(q.toString());
      }
    }

    const H = catalog.hashes || {};
    const dec = new TextDecoder("utf-8");
    const getInt = (name, def = 0) => {
      const h = H[name];
      if (h === undefined || !kv.has(h)) return def;
      return kv.get(h) | 0;
    };
    const getBool = (name) => {
      const h = H[name];
      return h !== undefined ? Boolean(kv.get(h) || 0) : false;
    };
    const getFloat = (name, def = 0.0) => {
      const h = H[name];
      if (h === undefined || !kv.has(h)) return def;
      const tmp = new DataView(new ArrayBuffer(4));
      tmp.setUint32(0, kv.get(h), true);
      return tmp.getFloat32(0, true);
    };
    const getStr = (name) => {
      const h = H[name];
      if (h === undefined) return "";
      const off = kv.get(h) || 0;
      if (off === 0 || off >= bytes.length) return "";
      let end = off;
      const maxEnd = Math.min(bytes.length, off + 128);
      while (end < maxEnd && bytes[end] !== 0) end++;
      return end < maxEnd ? dec.decode(bytes.subarray(off, end)) : "";
    };
    const getVec3 = (name) => {
      const h = H[name];
      if (h === undefined) return null;
      const off = kv.get(h) || 0;
      if (off === 0 || off + 12 > bytes.length) return null;
      const x = dv.getFloat32(off, true);
      const y = dv.getFloat32(off + 4, true);
      const z = dv.getFloat32(off + 8, true);
      if (![x, y, z].every(Number.isFinite)) return null;
      return [Math.round(x * 1000) / 1000, Math.round(y * 1000) / 1000, Math.round(z * 1000) / 1000];
    };

    const scene = getStr("Sequence_CurrentBanc");
    const isChild = getBool("Sequence_IsChildhood");
    const pos = getVec3("Player_Pos_For_Map");
    const rot = Math.round(-getFloat("Player_Rot_For_Map", 0.0) * 100) / 100 || 0;
    const [placeId, floorId] = resolvePlaceAndFloorClient(scene, pos, isChild, catalog);
    const projected = projectPlayerPositionsClient(scene, placeId, floorId, pos, catalog);

    const collected = {};
    const byCat = {};
    for (const it of catalog.collectibles || []) {
      const rule = it.rule || {};
      let done = false;
      if (rule.type === "b64") done = b64Set.has(String(rule.hash));
      else if (rule.type === "bool32") done = getBool(rule.flag);
      else if (rule.type === "bool32_any") done = (rule.flags || []).some((fl) => getBool(fl));
      else if (rule.type === "int_gte") done = getInt(rule.flag, 0) >= Number(rule.target || 0);
      collected[it.id] = done;
      if (!byCat[it.cat]) byCat[it.cat] = { collected: 0, total: 0 };
      byCat[it.cat].total += 1;
      if (done) byCat[it.cat].collected += 1;
    }

    const bottlesOwned = [
      "kakariko-bottle-01",
      "lonlon-bottle-01",
      "lago-bottle-01",
      "ciudadela-bottle-01",
      "ciudadela-bottle-02",
    ].filter((bid) => collected[bid]).length;

    const lifeQ = getInt("PlayerStatus.Life", 12);
    const maxLifeQ = getInt("PlayerStatus.MaxLife", 12);
    return {
      save_path: fileName,
      mtime_ns: Math.round(lastModifiedMs * 1e6),
      last_modified: new Date(lastModifiedMs).toISOString(),
      player: {
        scene,
        place: placeId,
        floor: floorId,
        age: isChild ? "child" : "adult",
        pos,
        rot,
        projected,
      },
      summary: {
        hearts: Math.round((lifeQ / 4.0) * 100) / 100,
        max_hearts: Math.round((maxLifeQ / 4.0) * 100) / 100,
        heart_pieces_in_pouch: getInt("PouchData.Obj_Heart_Piece.StockNum", 0),
        rupees: getInt("PlayerStatus.CurrentRupee", 0),
        tokens: getInt("PouchData.Item_Token_Gold.StockNum", 0),
        bottles: bottlesOwned,
        stones: {
          kokiri: getBool("IsGet.Item_Stone_Forest"),
          goron: getBool("IsGet.Item_Stone_Fire"),
          zora: getBool("IsGet.Item_Stone_Water"),
        },
        medallions: {
          light: getBool("IsGet.Item_Medal_Light"),
          forest: getBool("IsGet.Item_Medal_Forest"),
          fire: getBool("IsGet.Item_Medal_Fire"),
          water: getBool("IsGet.Item_Medal_Water"),
          shadow: getBool("IsGet.Item_Medal_Shadow"),
          spirit: getBool("IsGet.Item_Medal_Spirit"),
        },
        equipment: {
          ocarina_fairy: getBool("IsGet.Item_Ocarina_Fairy"),
          ocarina_time: getBool("IsGet.Item_Ocarina_Time"),
          slingshot: getBool("IsGet.Weapon_Range_SlingShot"),
          boomerang: getBool("IsGet.Item_Boomerang"),
          bombs: getBool("IsGet.Item_BombBag_Small"),
          bow: getBool("IsGet.Weapon_Range_Bow"),
          hookshot: getBool("IsGet.Item_Hookshot"),
          longshot: getBool("IsGet.Item_Longshot"),
          hammer: getBool("IsGet.Item_Hammer"),
          lens: getBool("IsGet.Armor_Adult_GlassTruth") || getBool("IsGet.Armor_Child_GlassTruth") || getBool("IsGet.Item_LensOfTruth"),
          iron_boots: getBool("IsGet.Armor_Adult_HeavyBoot"),
          hover_boots: getBool("IsGet.Armor_Adult_HoverBoot"),
          goron_tunic: getBool("IsGet.Armor_Adult_Goron"),
          zora_tunic: getBool("IsGet.Armor_Adult_Zora"),
          silver_scale: getBool("IsGet.Item_Scale_Silver"),
          gold_scale: getBool("IsGet.Item_Scale_Gold"),
          goron_bracelet: getBool("IsGet.Armor_Child_Gauntlet_Goron"),
          silver_gauntlets: getBool("IsGet.Armor_Adult_Gauntlet_Silver"),
          gold_gauntlets: getBool("IsGet.Armor_Adult_Gauntlet_Gold"),
          mirror_shield: getBool("Weapon_Shield_Mirror") || getBool("IsGet.Weapon_Shield_Mirror"),
          gerudo_token: getBool("IsGet.Item_Token_Gerudo"),
        },
      },
      collected,
      counts: {
        collected: Object.values(collected).filter(Boolean).length,
        total: (catalog.collectibles || []).length,
        by_cat: byCat,
      },
    };
  }

  function extractCaptionThumbnailUrl(arrayBuffer) {
    const bytes = new Uint8Array(arrayBuffer);
    let start = -1;
    for (let i = 0; i <= bytes.length - 3; i++) {
      if (bytes[i] === 0xff && bytes[i + 1] === 0xd8 && bytes[i + 2] === 0xff) {
        start = i;
        break;
      }
    }
    if (start === -1) return null;
    let end = bytes.length;
    for (let i = bytes.length - 2; i > start; i--) {
      if (bytes[i] === 0xff && bytes[i + 1] === 0xd9) {
        end = i + 2;
        break;
      }
    }
    const blob = new Blob([bytes.subarray(start, end)], { type: "image/jpeg" });
    return URL.createObjectURL(blob);
  }

  function openHandleDb() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) {
        reject(new Error("IndexedDB unavailable"));
        return;
      }
      const req = indexedDB.open("oot_map_web_db", 1);
      req.onupgradeneeded = () => {
        if (!req.result.objectStoreNames.contains("handles")) {
          req.result.createObjectStore("handles");
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function idbGetSavedDirHandle() {
    try {
      const db = await openHandleDb();
      return await new Promise((resolve) => {
        const tx = db.transaction("handles", "readonly");
        const req = tx.objectStore("handles").get("save_dir");
        req.onsuccess = () => resolve(req.result || null);
        req.onerror = () => resolve(null);
      });
    } catch {
      return null;
    }
  }

  async function idbSetSavedDirHandle(handle) {
    try {
      const db = await openHandleDb();
      await new Promise((resolve) => {
        const tx = db.transaction("handles", "readwrite");
        if (handle) tx.objectStore("handles").put(handle, "save_dir");
        else tx.objectStore("handles").delete("save_dir");
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      });
    } catch {
      // ignore IndexedDB errors
    }
  }

  const webSync = {
    dirHandle: null,
    pendingDirHandle: null,
    dirName: "",
    pollTimer: null,
    scanning: false,
    slotCache: new Map(), // key -> { lastModified, size, parsed, slotInfo, capLastModified, thumbUrl }
    lastSignature: "",
  };

  function clearWebSlotCache() {
    for (const entry of webSync.slotCache.values()) {
      if (entry.thumbUrl) {
        try { URL.revokeObjectURL(entry.thumbUrl); } catch {}
      }
    }
    webSync.slotCache.clear();
    webSync.lastSignature = "";
  }

  async function inspectWebSlotHandle(profileId, slotName, slotDirHandle, relLabel) {
    let savHandle = null;
    try {
      savHandle = await slotDirHandle.getFileHandle("progress.sav");
    } catch {
      return null;
    }
    const savFile = await savHandle.getFile();
    const key = `${profileId}/${slotName}`;
    const prev = webSync.slotCache.get(key);

    let parsed = prev?.parsed || null;
    let slotInfo = prev?.slotInfo || null;
    if (!prev || prev.lastModified !== savFile.lastModified || prev.size !== savFile.size) {
      let lastErr = null;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const buf = await savFile.arrayBuffer();
          parsed = parseProgressSavBuffer(buf, state.catalog, relLabel, savFile.lastModified);
          lastErr = null;
          break;
        } catch (err) {
          lastErr = err;
          await new Promise((r) => setTimeout(r, 50));
        }
      }
      if (lastErr || !parsed) return prev ? { parsed: prev.parsed, slotInfo: prev.slotInfo } : null;
    }

    let thumbUrl = prev?.thumbUrl || null;
    let capLastModified = prev?.capLastModified || 0;
    try {
      const capHandle = await slotDirHandle.getFileHandle("caption.sav");
      const capFile = await capHandle.getFile();
      if (!thumbUrl || capFile.lastModified !== capLastModified) {
        const capBuf = await capFile.arrayBuffer();
        const nextUrl = extractCaptionThumbnailUrl(capBuf);
        if (nextUrl) {
          if (thumbUrl) {
            try { URL.revokeObjectURL(thumbUrl); } catch {}
          }
          thumbUrl = nextUrl;
          capLastModified = capFile.lastModified;
        }
      }
    } catch {
      // optional caption.sav
    }

    slotInfo = {
      profile: profileId,
      slot: slotName,
      progress_path: relLabel,
      has_thumbnail: Boolean(thumbUrl),
      thumb_url: thumbUrl,
      mtime_ns: parsed.mtime_ns,
      last_modified: parsed.last_modified,
      scene: parsed.player.scene,
      place: parsed.player.place,
      age: parsed.player.age,
      tokens: parsed.summary.tokens,
      max_hearts: parsed.summary.max_hearts,
      collected_count: parsed.counts.collected,
      total_count: parsed.counts.total,
    };

    webSync.slotCache.set(key, {
      lastModified: savFile.lastModified,
      size: savFile.size,
      parsed,
      slotInfo,
      capLastModified,
      thumbUrl,
    });
    return { parsed, slotInfo };
  }

  async function scanWebDirectoryHandle(dirHandle) {
    if (!state.catalog || webSync.scanning) return;
    webSync.scanning = true;
    try {
      const profiles = [];
      const parsedMap = new Map();

      // Case 1: dirHandle itself contains progress.sav
      const directItem = await inspectWebSlotHandle("direct", dirHandle.name || "save", dirHandle, `${dirHandle.name}/progress.sav`);
      if (directItem) {
        parsedMap.set(`direct/${directItem.slotInfo.slot}`, directItem.parsed);
        profiles.push({ id: "direct", path: dirHandle.name, slots: [directItem.slotInfo] });
      } else {
        const subDirs = [];
        for await (const entry of dirHandle.values()) {
          if (entry.kind === "directory") subDirs.push(entry);
        }
        subDirs.sort((a, b) => a.name.localeCompare(b.name));

        // Case 2: dirHandle directly contains slot_XX/progress.sav
        const directSlots = [];
        for (const sub of subDirs) {
          const item = await inspectWebSlotHandle("default", sub.name, sub, `${dirHandle.name}/${sub.name}/progress.sav`);
          if (item) {
            parsedMap.set(`default/${sub.name}`, item.parsed);
            directSlots.push(item.slotInfo);
          }
        }
        if (directSlots.length) {
          profiles.push({ id: "default", path: dirHandle.name, slots: directSlots });
        } else {
          // Case 3: dirHandle contains <profile>/slot_XX/progress.sav
          for (const profDir of subDirs) {
            const slotDirs = [];
            for await (const sub of profDir.values()) {
              if (sub.kind === "directory") slotDirs.push(sub);
            }
            slotDirs.sort((a, b) => a.name.localeCompare(b.name));
            const profSlots = [];
            for (const sDir of slotDirs) {
              const item = await inspectWebSlotHandle(
                profDir.name,
                sDir.name,
                sDir,
                `${dirHandle.name}/${profDir.name}/${sDir.name}/progress.sav`
              );
              if (item) {
                parsedMap.set(`${profDir.name}/${sDir.name}`, item.parsed);
                profSlots.push(item.slotInfo);
              }
            }
            if (profSlots.length) {
              profiles.push({ id: profDir.name, path: profDir.name, slots: profSlots });
            }
          }
        }
      }

      applyWebDiscoveredProfiles(profiles, parsedMap, true, dirHandle.name);
    } finally {
      webSync.scanning = false;
    }
  }

  function applyWebDiscoveredProfiles(profiles, parsedMap, isLiveWatch, rootLabel) {
    const allSlots = profiles.flatMap((p) => p.slots || []);
    const autoFollow = Boolean(state.serverState?.config?.auto_follow_slot);
    let chosenSlot = null;
    if (allSlots.length) {
      if (autoFollow) {
        chosenSlot = allSlots.reduce((best, s) => ((s.mtime_ns || 0) > (best.mtime_ns || 0) ? s : best), allSlots[0]);
      } else {
        const curProf = state.serverState?.config?.profile;
        const curSlot = state.serverState?.config?.slot;
        chosenSlot = allSlots.find((s) => s.profile === curProf && s.slot === curSlot)
          || allSlots.reduce((best, s) => ((s.mtime_ns || 0) > (best.mtime_ns || 0) ? s : best), allSlots[0]);
      }
    }

    const chosenParsed = chosenSlot ? (parsedMap.get(`${chosenSlot.profile}/${chosenSlot.slot}`) || null) : null;
    const sig = JSON.stringify({
      rootLabel,
      isLiveWatch,
      autoFollow,
      chosenKey: chosenSlot ? `${chosenSlot.profile}/${chosenSlot.slot}:${chosenSlot.mtime_ns}` : "",
      slots: allSlots.map((s) => `${s.profile}/${s.slot}:${s.mtime_ns}:${s.collected_count}`),
    });

    if (sig === webSync.lastSignature && state.serverState?.save === chosenParsed) {
      return;
    }
    webSync.lastSignature = sig;

    if (chosenParsed) {
      // Cache lightweight snapshot (without huge cache bloat) in localStorage only if needed
      try {
        writeLocalJson(WEB_STORAGE_KEYS.save, chosenParsed);
      } catch {}
    }

    const nextState = {
      ...state.serverState,
      config: {
        ...(state.serverState?.config || {}),
        save_root: rootLabel || "",
        profile: chosenSlot?.profile || null,
        slot: chosenSlot?.slot || null,
        auto_follow_slot: autoFollow,
      },
      sync: {
        mode: isLiveWatch ? (chosenParsed ? "web_watch" : "web_manual") : (chosenParsed ? "web_save" : "web_manual"),
        process_running: false,
        process_name: null,
        memory_attached: false,
      },
      discovery: {
        save_root: rootLabel || "",
        exists: true,
        profiles,
      },
      save: chosenParsed,
    };
    handleServerState(nextState, false);
  }

  async function startWebDirectorySync(dirHandle) {
    stopWebDirectorySync(false);
    webSync.dirHandle = dirHandle;
    webSync.pendingDirHandle = null;
    webSync.dirName = dirHandle.name || "save";
    await idbSetSavedDirHandle(dirHandle);
    await scanWebDirectoryHandle(dirHandle);
    webSync.pollTimer = setInterval(() => {
      if (webSync.dirHandle && !document.hidden) {
        scanWebDirectoryHandle(webSync.dirHandle).catch((err) => console.warn("Folder poll:", err));
      }
    }, 800);
  }

  function stopWebDirectorySync(clearSavedHandle = true) {
    if (webSync.pollTimer) {
      clearInterval(webSync.pollTimer);
      webSync.pollTimer = null;
    }
    webSync.dirHandle = null;
    webSync.dirName = "";
    clearWebSlotCache();
    if (clearSavedHandle) {
      webSync.pendingDirHandle = null;
      idbSetSavedDirHandle(null);
    }
  }

  async function scanWebFileList(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length || !state.catalog) return;
    stopWebDirectorySync(true);

    const byDir = new Map();
    for (const f of files) {
      const rel = (f.webkitRelativePath || f.name).replace(/\\/g, "/");
      const parts = rel.split("/").filter(Boolean);
      const fname = parts[parts.length - 1];
      if (fname !== "progress.sav" && fname !== "caption.sav") continue;
      const dirKey = parts.slice(0, -1).join("/");
      if (!byDir.has(dirKey)) byDir.set(dirKey, { parts: parts.slice(0, -1) });
      byDir.get(dirKey)[fname] = f;
    }

    const rootName = (files[0].webkitRelativePath || "").split("/")[0] || "save";
    const profilesMap = new Map();
    const parsedMap = new Map();

    for (const [dirKey, entry] of [...byDir.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
      const savFile = entry["progress.sav"];
      if (!savFile) continue;
      const p = entry.parts;
      let profileId = "default";
      let slotName = rootName;
      if (p.length <= 1) {
        profileId = "direct";
        slotName = p[0] || rootName;
      } else if (p.length === 2) {
        profileId = "default";
        slotName = p[1];
      } else {
        profileId = p[p.length - 2];
        slotName = p[p.length - 1];
      }

      try {
        const parsed = parseProgressSavBuffer(await savFile.arrayBuffer(), state.catalog, `${dirKey}/progress.sav`, savFile.lastModified);
        let thumbUrl = null;
        if (entry["caption.sav"]) {
          thumbUrl = extractCaptionThumbnailUrl(await entry["caption.sav"].arrayBuffer());
        }
        const slotInfo = {
          profile: profileId,
          slot: slotName,
          progress_path: `${dirKey}/progress.sav`,
          has_thumbnail: Boolean(thumbUrl),
          thumb_url: thumbUrl,
          mtime_ns: parsed.mtime_ns,
          last_modified: parsed.last_modified,
          scene: parsed.player.scene,
          place: parsed.player.place,
          age: parsed.player.age,
          tokens: parsed.summary.tokens,
          max_hearts: parsed.summary.max_hearts,
          collected_count: parsed.counts.collected,
          total_count: parsed.counts.total,
        };
        if (!profilesMap.has(profileId)) profilesMap.set(profileId, { id: profileId, path: profileId, slots: [] });
        profilesMap.get(profileId).slots.push(slotInfo);
        parsedMap.set(`${profileId}/${slotName}`, parsed);
        webSync.slotCache.set(`${profileId}/${slotName}`, {
          lastModified: savFile.lastModified,
          size: savFile.size,
          parsed,
          slotInfo,
          capLastModified: 0,
          thumbUrl,
        });
      } catch (err) {
        console.warn("Skip unreadable save:", dirKey, err);
      }
    }

    webSync.dirName = rootName;
    applyWebDiscoveredProfiles([...profilesMap.values()], parsedMap, false, rootName);
  }

  const $ = (id) => document.getElementById(id);

  function t(key) {
    return state.catalog?.i18n?.ui?.[state.lang]?.[key] || key;
  }

  function locText(obj, fallback = "") {
    if (!obj) return fallback;
    if (typeof obj === "string") return obj;
    return obj[state.lang] || obj["en"] || obj["zh-CN"] || fallback;
  }

  function resolveImageUrl(relPath) {
    if (!relPath) return "";
    return "/maps/" + relPath.replace(/^maps\//, "");
  }

  function isCollected(itemId) {
    const ov = state.serverState?.overrides?.checks;
    if (ov && Object.prototype.hasOwnProperty.call(ov, itemId)) {
      return Boolean(ov[itemId]);
    }
    return Boolean(state.serverState?.save?.collected?.[itemId]);
  }

  function isSavedCollected(itemId) {
    return Boolean(state.serverState?.save?.collected?.[itemId]);
  }

  function matchesEra(it, era) {
    if (!era || era === "all") return true;
    if (era === "child") {
      if (ADULT_ONLY_PLACES.has(it.place)) return false;
      return it.age !== "adult";
    }
    if (era === "adult") {
      if (CHILD_ONLY_PLACES.has(it.place)) return false;
      return it.age !== "child";
    }
    return true;
  }

  function detectPlayerEra(player) {
    if (!player) return null;
    if (player.scene && player.scene.includes("_Adult")) return "adult";
    if (player.scene && player.scene.endsWith("_Child")) return "child";
    if (ADULT_ONLY_PLACES.has(player.place)) return "adult";
    if (CHILD_ONLY_PLACES.has(player.place)) return "child";
    return null;
  }

  function getFilteredItems() {
    if (!state.catalog) return [];
    const q = state.search.trim().toLowerCase();
    return state.catalog.collectibles.filter((it) => {
      if (state.activeCategoryFilter && it.cat !== state.activeCategoryFilter) return false;
      const done = isCollected(it.id);
      if (state.filterStatus === "remaining" && done) return false;
      if (state.filterStatus === "done" && !done) return false;
      if (state.filterAge === "child" || state.filterAge === "adult") {
        if (!matchesEra(it, state.filterAge)) return false;
      } else if (state.filterAge === "night" && !it.night) {
        return false;
      }
      if (q) {
        const place = state.catalog.places.find((p) => p.id === it.place);
        const hay = [
          it.id,
          locText(it.title),
          locText(it.hint),
          locText(it.guide),
          place ? locText(place.name) : "",
          ...it.requires
            .flatMap((rk) => (Array.isArray(rk) ? rk : [rk]))
            .map((rk) => locText(state.catalog.requirements[rk])),
        ]
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function getPlaceById(pid) {
    return state.catalog?.places?.find((p) => p.id === pid) || null;
  }

  function getCategoryByKey(key) {
    return state.catalog?.categories?.find((c) => c.key === key) || null;
  }

  function formatSceneName(scene) {
    if (!scene) return "-";
    const base = scene.replace("_Child", "").replace("_Adult_Alternative", "").replace("_Adult", "");
    const locObj = state.catalog?.i18n?.locations?.[base];
    const label = locObj ? locText(locObj, base) : scene;
    if (scene.endsWith("_Child")) return `${label} (${t("ageChild")})`;
    if (scene.includes("_Adult")) return `${label} (${t("ageAdult")})`;
    return label;
  }

  function updateEraSwitchUi() {
    if (!state.catalog) return;
    const cols = state.catalog.collectibles;
    const childItems = cols.filter((it) => matchesEra(it, "child"));
    const adultItems = cols.filter((it) => matchesEra(it, "adult"));
    const childDone = childItems.filter((it) => isCollected(it.id)).length;
    const adultDone = adultItems.filter((it) => isCollected(it.id)).length;
    const allDone = cols.filter((it) => isCollected(it.id)).length;

    const lbl = {
      "zh-CN": { child: "少年地图", adult: "青年地图", all: "全部", cBadge: "少年时代 · Child Hyrule", aBadge: "青年时代 · Adult Hyrule", allBadge: "全时期 · All Eras" },
      "ja":    { child: "子供マップ", adult: "大人マップ", all: "すべて", cBadge: "子供時代 · Child Hyrule", aBadge: "大人時代 · Adult Hyrule", allBadge: "全時代 · All Eras" },
      "en":    { child: "Child Map", adult: "Adult Map", all: "All", cBadge: "Child Era · Hyrule", aBadge: "Adult Era · Hyrule", allBadge: "All Eras · Hyrule" },
    }[state.lang] || { child: "Child Map", adult: "Adult Map", all: "All", cBadge: "Child Era", aBadge: "Adult Era", allBadge: "All Eras" };

    $("btnEraChild").textContent = `${lbl.child} ${childDone}/${childItems.length}`;
    $("btnEraAdult").textContent = `${lbl.adult} ${adultDone}/${adultItems.length}`;
    $("btnEraAll").textContent = `${lbl.all} ${allDone}/${cols.length}`;

    document.querySelectorAll(".era-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.era === state.overworldEra);
    });

    const vp = $("mapViewport");
    vp.classList.remove("era-child", "era-adult", "era-all");
    vp.classList.add(`era-${state.overworldEra}`);

    const badge = $("eraCornerBadge");
    badge.classList.toggle("hidden", state.viewMode !== "overworld");
    badge.textContent =
      state.overworldEra === "child" ? lbl.cBadge :
      state.overworldEra === "adult" ? lbl.aBadge : lbl.allBadge;
  }

  function applyStaticI18n() {
    if (!state.catalog) return;
    $("appTitle").textContent = t("appTitle");
    $("appSubtitle").textContent = t("appSubtitle");
    $("btnOverworld").textContent = t("navOverworld");
    $("tabPlaces").textContent = t("navPlaces");
    $("tabItems").textContent = t("navItems");
    $("lblSaveSection").textContent = t("savePathLabel");
    $("inputSavePath").placeholder = t("savePathPlaceholder");
    $("btnBrowseDir").textContent = t("browseBtn");
    $("btnRescan").textContent = t("rescanBtn");
    $("lblAutoSlot").textContent = t("autoFollowSlot");
    $("lblAutoMap").textContent = t("autoFollowMap");
    $("lblHeroScene").textContent = t("heroScene");
    $("lblHeroFloor").textContent = t("heroFloor");
    $("lblHeroPos").textContent = t("heroPos");
    $("lblTotalProgress").textContent = t("progressTotal");
    $("lblPouchSummary").textContent = t("pouchSummary");
    $("lblHearts").textContent = t("hearts");
    $("lblTokens").textContent = t("tokens");
    $("lblBottles").textContent = t("bottles");
    $("searchInput").placeholder = t("searchPlaceholder");
    const toggleLabelsMap = { "zh-CN": "地名进度", "ja": "進捗表示", "en": "Progress" };
    $("btnToggleLabels").textContent = toggleLabelsMap[state.lang] || "Progress";
    $("btnCenterLink").textContent = t("centerOnLink");
    $("btnResetZoom").textContent = t("resetZoom");
    $("lblDetailReq").textContent = t("reqLabel");
    $("lblDetailGuide").textContent = t("guideTitle");
    $("lblDetailTech").textContent = t("saveFlagLabel");
    $("lblCoords").textContent = t("coordsLabel");
    $("lblSaveFlag").textContent = t("saveFlagLabel");
    $("lblManualOverride").textContent = t("manualCheckLabel");
    $("txtItemNote").placeholder = t("notePlaceholder");
    $("lblBrowseTitle").textContent = t("browseModalTitle");
    $("btnBrowseSelect").textContent = t("browseSelectCurrent");
    $("btnBrowseCancel").textContent = t("browseCancel");
    $("btnBrowseUp").textContent = t("browseParent");
    $("noMapText").textContent = t("noPlaceMap");
    $("btnBackToOverworld").textContent = t("navOverworld");

    const webLabels = {
      "zh-CN": {
        pickDir: "选择存档目录",
        resumeDir: (d) => `恢复目录同步 (${d})`,
        clear: "清除同步/存档",
        reset: "重置勾选",
        hintEmpty: "点击「选择存档目录」选择游戏的存档目录（如 longshot\\...\\user 或 save），即可自动识别并实时同步最新存档。",
        hintWatch: (d) => `实时同步中：${d}（自动追踪最新修改的 progress.sav）`,
        hintPending: (d) => `上次已授权文件夹「${d}」，点击上方按钮即可恢复实时同步。`,
        hintSave: (name) => `已载入：${name}（浏览器本地解析，不上传服务器）`,
        resetModalTitle: "重置勾选说明",
        resetModalCancel: "取消",
        resetModalConfirm: "确认重置",
        mobTabMap: "地图",
        mobTabList: "列表·存档",
        mobTabDetail: "攻略详情",
        drawerHeading: "详情与攻略",
        drawerBtn: "详情攻略",
        mqGuide: "完整详情",
      },
      "ja": {
        pickDir: "リアルタイム同期フォルダ",
        resumeDir: (d) => `同期を再開 (${d})`,
        clear: "同期/セーブ解除",
        reset: "手動チェック初期化",
        hintEmpty: "「リアルタイム同期フォルダ」からゲームのセーブフォルダ（user / save）を選択すると、最新のセーブを自動追跡します。",
        hintWatch: (d) => `リアルタイム同期中：${d}（最新の progress.sav を自動追跡）`,
        hintPending: (d) => `前回のフォルダ「${d}」の同期を再開できます。`,
        hintSave: (name) => `読込済：${name}（ブラウザ内のみで解析）`,
        resetModalTitle: "手動チェックの初期化について",
        resetModalCancel: "キャンセル",
        resetModalConfirm: "リセットする",
        mobTabMap: "マップ",
        mobTabList: "リスト",
        mobTabDetail: "詳細・攻略",
        drawerHeading: "詳細・攻略",
        drawerBtn: "詳細",
        mqGuide: "詳細",
      },
      "en": {
        pickDir: "Live Sync Folder",
        resumeDir: (d) => `Resume Folder Sync (${d})`,
        clear: "Clear Save/Sync",
        reset: "Reset Checks",
        hintEmpty: "Click 'Live Sync Folder' and pick your save directory (e.g. user or save) to auto-track the latest save in real time.",
        hintWatch: (d) => `Live syncing folder: ${d} (auto-tracking newest progress.sav)`,
        hintPending: (d) => `Click Resume Sync above to reconnect "${d}".`,
        hintSave: (name) => `Loaded locally: ${name} (parsed in browser only)`,
        resetModalTitle: "About Reset Checks",
        resetModalCancel: "Cancel",
        resetModalConfirm: "Confirm Reset",
        mobTabMap: "Map",
        mobTabList: "List & Save",
        mobTabDetail: "Guide",
        drawerHeading: "Item & Guide",
        drawerBtn: "Guide",
        mqGuide: "Details",
      },
    }[state.lang] || {
      pickDir: "Live Sync Folder",
      resumeDir: (d) => `Resume Sync (${d})`,
      clear: "Clear Save/Sync",
      reset: "Reset Checks",
      hintEmpty: "Click 'Live Sync Folder' to select your save directory.",
      hintWatch: (d) => `Live syncing: ${d}`,
      hintPending: (d) => `Resume "${d}"`,
      hintSave: (name) => `Loaded: ${name}`,
      resetModalTitle: "About Reset Checks",
      resetModalCancel: "Cancel",
      resetModalConfirm: "Confirm Reset",
      mobTabMap: "Map",
      mobTabList: "List & Save",
      mobTabDetail: "Guide",
      drawerHeading: "Item & Guide",
      drawerBtn: "Guide",
      mqGuide: "Details",
    };
    if ($("btnPickWebDir")) $("btnPickWebDir").textContent = webLabels.pickDir;
    if ($("btnResumeWebDir") && webSync.pendingDirHandle) {
      $("btnResumeWebDir").textContent = webLabels.resumeDir(webSync.pendingDirHandle.name || "save");
    }
    if ($("btnClearWebSave")) $("btnClearWebSave").textContent = webLabels.clear;
    if ($("btnResetWebChecks")) $("btnResetWebChecks").textContent = webLabels.reset;
    if ($("lblResetModalTitle")) $("lblResetModalTitle").textContent = webLabels.resetModalTitle;
    if ($("btnResetModalCancel")) $("btnResetModalCancel").textContent = webLabels.resetModalCancel;
    if ($("btnResetModalConfirm")) $("btnResetModalConfirm").textContent = webLabels.resetModalConfirm;
    if ($("lblMobTabMap")) $("lblMobTabMap").textContent = webLabels.mobTabMap;
    if ($("lblMobTabList")) $("lblMobTabList").textContent = webLabels.mobTabList;
    if ($("lblMobTabDetail")) $("lblMobTabDetail").textContent = webLabels.mobTabDetail;
    if ($("lblDrawerHeading")) $("lblDrawerHeading").textContent = webLabels.drawerHeading;
    if ($("btnToggleDetailDrawer")) $("btnToggleDetailDrawer").textContent = webLabels.drawerBtn;
    if ($("btnMqGuide")) $("btnMqGuide").textContent = webLabels.mqGuide;
    if ($("webSaveHint")) {
      const saveName = state.serverState?.save?.save_path;
      if (webSync.dirHandle) {
        $("webSaveHint").textContent = webLabels.hintWatch(webSync.dirName || webSync.dirHandle.name);
      } else if (webSync.pendingDirHandle) {
        $("webSaveHint").textContent = webLabels.hintPending(webSync.pendingDirHandle.name || "save");
      } else {
        $("webSaveHint").textContent = saveName ? webLabels.hintSave(saveName) : webLabels.hintEmpty;
      }
    }

    const fs = $("filterStatus");
    fs.options[0].text = t("filterAll");
    fs.options[1].text = t("filterRemaining");
    fs.options[2].text = t("filterDone");

    const fa = $("filterAge");
    fa.options[0].text = t("filterAgeAll");
    fa.options[1].text = t("ageChild");
    fa.options[2].text = t("ageAdult");
    fa.options[3].text = t("filterNightOnly");

    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === state.lang);
    });
  }

  function getCurrentPlayer(ss = state.serverState) {
    return ss?.save?.player || ss?.live_player || null;
  }

  function renderHeaderSyncAndTelemetry() {
    const ss = state.serverState;
    const sync = ss?.sync || { mode: "no_save" };
    const pill = $("syncPill");
    pill.className = `sync-pill mode-${sync.mode}`;
    if (sync.mode === "live_memory") {
      $("syncText").textContent = `${t("syncLiveMem")} (${sync.process_name || "longshot.exe"})`;
    } else if (sync.mode === "save_watch") {
      $("syncText").textContent = t("syncSaveWatch");
    } else if (sync.mode === "web_watch") {
      $("syncText").textContent = { "zh-CN": "在线版 · 文件夹实时同步中", "ja": "Web版 · フォルダ同期中", "en": "Web · Live Folder Sync" }[state.lang] || "Web · Live Folder Sync";
    } else if (sync.mode === "web_save") {
      $("syncText").textContent = { "zh-CN": "在线版 · 已导入存档", "ja": "Web版 · セーブ読込済", "en": "Web · Save Loaded" }[state.lang] || "Web · Save Loaded";
    } else if (sync.mode === "web_manual") {
      $("syncText").textContent = { "zh-CN": "在线版 · 浏览器本地记录", "ja": "Web版 · ローカル記録", "en": "Web · Local Tracker" }[state.lang] || "Web · Local Tracker";
    } else {
      $("syncText").textContent = t("noSaveLoaded");
    }

    const player = getCurrentPlayer(ss);
    if (player) {
      $("valHeroScene").textContent = formatSceneName(player.scene);
      const pl = getPlaceById(player.place);
      const flObj = pl?.maps?.find((m) => m.id === player.floor);
      $("valHeroFloor").textContent = flObj ? locText(flObj.label) : (player.floor || "-");
      $("valHeroPos").textContent = player.pos ? `${player.pos[0].toFixed(1)}, ${player.pos[1].toFixed(1)}, ${player.pos[2].toFixed(1)}` : "-";
    } else {
      $("valHeroScene").textContent = "-";
      $("valHeroFloor").textContent = "-";
      $("valHeroPos").textContent = "-";
    }

    const total = state.catalog?.collectibles?.length || 188;
    const done = state.catalog
      ? state.catalog.collectibles.filter((it) => isCollected(it.id)).length
      : 0;
    $("valTotalProgress").textContent = `${done} / ${total}`;
    $("barTotalProgress").style.width = `${Math.round((done / total) * 100)}%`;
  }

  function renderSaveSlotsAndPouch() {
    const ss = state.serverState;
    if (!ss) return;
    if (state.staticMode) {
      $("webSaveBox")?.classList.remove("hidden");
      $("btnResumeWebDir")?.classList.toggle("hidden", !webSync.pendingDirHandle || Boolean(webSync.dirHandle));
      $("btnClearWebSave")?.classList.toggle("hidden", !ss.save && !webSync.dirHandle && !(ss.discovery?.profiles?.length));
      applyStaticI18n();
    }
    if (document.activeElement !== $("inputSavePath")) {
      $("inputSavePath").value = ss.config?.save_root || "";
    }
    $("chkAutoSlot").checked = Boolean(ss.config?.auto_follow_slot);

    const cont = $("slotsContainer");
    cont.innerHTML = "";
    const profiles = ss.discovery?.profiles || [];
    const activeProf = ss.config?.profile;
    const activeSlot = ss.config?.slot;

    if (!profiles.length) {
      const empty = document.createElement("div");
      empty.className = "slot-sub";
      empty.textContent = t("noSaveLoaded");
      cont.appendChild(empty);
    } else {
      for (const prof of profiles) {
        for (const sl of prof.slots || []) {
          const el = document.createElement("div");
          const isAct = prof.id === activeProf && sl.slot === activeSlot;
          el.className = "slot-item" + (isAct ? " active" : "");

          const img = document.createElement("img");
          img.className = "slot-thumb";
          if (sl.thumb_url) {
            img.src = sl.thumb_url;
          } else if (sl.has_thumbnail) {
            img.src = `${state.apiBase}/api/saves/thumbnail?profile=${encodeURIComponent(prof.id)}&slot=${encodeURIComponent(sl.slot)}&t=${sl.mtime_ns || 0}`;
          }
          img.alt = sl.slot;

          const meta = document.createElement("div");
          meta.className = "slot-meta";
          const row1 = document.createElement("div");
          row1.className = "slot-title-row";
          const label = profiles.length > 1 ? `${prof.id.slice(0, 6)} / ${sl.slot}` : sl.slot;
          row1.innerHTML = `<span>${label}</span><span>${sl.collected_count ?? "?"}/${sl.total_count ?? 188}</span>`;

          const row2 = document.createElement("div");
          row2.className = "slot-sub";
          const scName = formatSceneName(sl.scene || "");
          const dt = sl.last_modified ? new Date(sl.last_modified).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
          row2.textContent = `${scName} · 🕷${sl.tokens ?? 0} · ${dt}`;

          meta.appendChild(row1);
          meta.appendChild(row2);
          el.appendChild(img);
          el.appendChild(meta);
          el.addEventListener("click", () => selectSlot(prof.id, sl.slot));
          cont.appendChild(el);
        }
      }
    }

    const sum = ss.save?.summary;
    if (sum) {
      $("valHearts").textContent = `${sum.hearts}/${sum.max_hearts}`;
      $("valTokens").textContent = `${sum.tokens}/100`;
      $("valBottles").textContent = `${sum.bottles}/5`;
      $("valRupees").textContent = `${sum.rupees}`;

      const stonesEl = $("stonesRow");
      stonesEl.innerHTML = "";
      [
        ["kokiri", "#22c55e", "森"],
        ["goron", "#ef4444", "火"],
        ["zora", "#38bdf8", "水"],
      ].forEach(([k, col, ch]) => {
        const d = document.createElement("span");
        d.className = "relic-dot" + (sum.stones?.[k] ? " owned" : "");
        d.style.color = col;
        d.style.borderColor = col;
        d.textContent = ch;
        stonesEl.appendChild(d);
      });

      const medalsEl = $("medalsRow");
      medalsEl.innerHTML = "";
      [
        ["light", "#fde047", "光"],
        ["forest", "#22c55e", "森"],
        ["fire", "#ef4444", "炎"],
        ["water", "#38bdf8", "水"],
        ["shadow", "#a855f7", "暗"],
        ["spirit", "#f97316", "魂"],
      ].forEach(([k, col, ch]) => {
        const d = document.createElement("span");
        d.className = "relic-dot" + (sum.medallions?.[k] ? " owned" : "");
        d.style.color = col;
        d.style.borderColor = col;
        d.textContent = ch;
        medalsEl.appendChild(d);
      });
    } else {
      $("valHearts").textContent = "-";
      $("valTokens").textContent = "-";
      $("valBottles").textContent = "-";
      $("valRupees").textContent = "-";
    }
  }

  function renderCategories() {
    if (!state.catalog) return;
    const grid = $("categoriesGrid");
    grid.innerHTML = "";
    const activeEra = state.overworldEra || "all";
    for (const cat of state.catalog.categories) {
      const items = state.catalog.collectibles.filter((it) => it.cat === cat.key && matchesEra(it, activeEra));
      const done = items.filter((it) => isCollected(it.id)).length;
      const pct = items.length ? Math.round((done / items.length) * 100) : 0;
      const meta = CAT_META[cat.key] || { color: "#94a3b8", svg: "•" };

      const chip = document.createElement("div");
      chip.className =
        "cat-chip" +
        (state.activeCategoryFilter === cat.key ? " active" : "") +
        (items.length && done === items.length ? " done" : "");
      chip.innerHTML = `
        <div class="cat-chip-left">
          <span class="cat-svg" style="color:${meta.color}">${meta.svg}</span>
          <span class="cat-name">${locText(cat.name)}</span>
        </div>
        <span class="cat-count">${done}/${items.length}</span>
        <div class="cat-prog-bar" style="width:${pct}%"></div>
      `;
      chip.addEventListener("click", () => {
        state.activeCategoryFilter = state.activeCategoryFilter === cat.key ? null : cat.key;
        renderAllListsAndMap();
      });
      grid.appendChild(chip);
    }
  }

  function renderNavLists() {
    if (!state.catalog) return;
    const filtered = getFilteredItems();
    const linkPlace = getCurrentPlayer()?.place;
    const activeEra = state.overworldEra || "all";

    // Places list
    const plCont = $("placesList");
    plCont.innerHTML = "";
    const zones = state.catalog.places.filter((p) => p.kind === "zone");
    const dungeons = state.catalog.places.filter((p) => p.kind === "dungeon");

    const appendGroup = (title, list) => {
      const gt = document.createElement("div");
      gt.className = "group-title";
      gt.textContent = title;
      plCont.appendChild(gt);

      for (const p of list) {
        const placeAll = state.catalog.collectibles.filter((it) => it.place === p.id && matchesEra(it, activeEra));
        const placeFiltered = filtered.filter((it) => it.place === p.id);
        if (state.search.trim() && placeFiltered.length === 0 && !locText(p.name).toLowerCase().includes(state.search.trim().toLowerCase())) {
          continue;
        }
        const done = placeAll.filter((it) => isCollected(it.id)).length;
        const pct = placeAll.length ? Math.round((done / placeAll.length) * 100) : 0;
        const row = document.createElement("div");
        const isActive = state.viewMode === "place" && state.activePlaceId === p.id;
        row.className = "place-row" + (isActive ? " active" : "") + (linkPlace === p.id ? " has-link" : "");

        const cntBadge = placeAll.length
          ? `<span class="badge-count ${done === placeAll.length ? "complete" : ""}">${done}/${placeAll.length}</span>`
          : `<span class="badge-count">0/0</span>`;

        row.innerHTML = `<span class="item-row-title">${locText(p.name)}</span>${cntBadge}<div class="place-row-prog" style="width:${pct}%"></div>`;
        row.addEventListener("click", () => openPlace(p.id, null));
        plCont.appendChild(row);
      }
    };

    appendGroup(t("zonesTitle"), zones);
    appendGroup(t("dungeonsTitle"), dungeons);

    // Items list
    const itCont = $("itemsList");
    itCont.innerHTML = "";
    for (const it of filtered) {
      const done = isCollected(it.id);
      const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
      const pl = getPlaceById(it.place);
      const row = document.createElement("div");
      row.className = "item-row" + (done ? " collected" : "") + (state.selectedItemId === it.id ? " active" : "");
      row.innerHTML = `
        <div class="item-row-left">
          <span class="cat-svg" style="color:${meta.color}">${meta.svg}</span>
          <span class="item-row-title">${locText(it.title)}</span>
        </div>
        <span class="badge-count ${done ? "complete" : ""}">${pl ? locText(pl.name).slice(0, 6) : ""}</span>
      `;
      row.addEventListener("click", () => selectItem(it.id, true));
      itCont.appendChild(row);
    }
  }

  function refreshLinkOverlapClass() {
    const marker = $("linkMarker");
    if (!marker || marker.classList.contains("hidden")) return;
    if (state.viewMode !== "overworld" || !state.lastLinkOverworldUv || !state.catalog) {
      marker.classList.remove("above-banner");
      return;
    }
    const cw = Math.max(1, (state.mapBaseW || 6000) * state.scale);
    const ch = Math.max(1, (state.mapBaseH || 4364) * state.scale);
    const lx = state.lastLinkOverworldUv.x * cw;
    const ly = state.lastLinkOverworldUv.y * ch;
    const overlaps = state.catalog.places.some((p) => {
      if (!p.pin) return false;
      const px = p.pin.x * cw;
      const py = p.pin.y * ch;
      return Math.abs(lx - px) < 82 && Math.abs(ly - py) < 38;
    });
    marker.classList.toggle("above-banner", overlaps);
  }

  function applyMapTransform() {
    const w = Math.max(1, Math.round((state.mapBaseW || 1000) * state.scale));
    const h = Math.max(1, Math.round((state.mapBaseH || 700) * state.scale));
    const inner = $("mapCanvasInner");
    inner.style.width = `${w}px`;
    inner.style.height = `${h}px`;
    $("mapTransform").style.transform = `translate3d(${state.tx}px, ${state.ty}px, 0)`;
    refreshLinkOverlapClass();
  }

  function isMobileLayout() {
    return window.innerWidth <= 900;
  }

  function isTabletLayout() {
    return window.innerWidth > 900 && window.innerWidth <= 1180;
  }

  function isCompactDetailLayout() {
    return isMobileLayout() || isTabletLayout();
  }

  function pickNonBlockingDock(pinEl, item) {
    const vp = $("mapViewport");
    const rect = vp?.getBoundingClientRect();
    if (!rect || !rect.height) return "bottom";
    let relY = 0.5;
    if (pinEl) {
      const pRect = pinEl.getBoundingClientRect();
      relY = (pRect.top + pRect.height / 2 - rect.top) / rect.height;
    } else if (item?.at) {
      const cy = state.ty + item.at.y * (state.mapBaseH || 700) * state.scale;
      relY = cy / rect.height;
    }
    return relY > 0.52 ? "top" : "bottom";
  }

  function renderReqChips(reqEl, it, showNone = true) {
    if (!reqEl) return false;
    reqEl.innerHTML = "";
    const equip = state.serverState?.save?.summary?.equipment || {};
    if (!it.requires || !it.requires.length) {
      if (!showNone) return false;
      const span = document.createElement("span");
      span.className = "req-chip owned";
      span.textContent = t("noReq");
      reqEl.appendChild(span);
      return true;
    }
    const orSep = state.lang === "zh-CN" ? " 或 " : state.lang === "ja" ? " または " : " or ";
    for (const rk of it.requires) {
      const span = document.createElement("span");
      if (Array.isArray(rk)) {
        const owned = rk.some((sub) => Boolean(REQ_EQUIP_MAP[sub]?.(equip)));
        span.className = "req-chip" + (owned ? " owned" : "");
        span.textContent = rk
          .map((sub) => locText(state.catalog.requirements[sub], sub))
          .join(orSep);
      } else {
        const fn = REQ_EQUIP_MAP[rk];
        const owned = fn ? Boolean(fn(equip)) : false;
        span.className = "req-chip" + (owned ? " owned" : "");
        span.textContent = locText(state.catalog.requirements[rk], rk);
      }
      reqEl.appendChild(span);
    }
    return true;
  }

  function setTabletDrawerOpen(open) {
    state.drawerOpen = Boolean(open) && isTabletLayout();
    $("sidebarRight")?.classList.toggle("drawer-open", state.drawerOpen);
    $("tabletDrawerBackdrop")?.classList.toggle("hidden", !state.drawerOpen);
    $("btnToggleDetailDrawer")?.classList.toggle("active", state.drawerOpen);
    updateMobileQuickCard();
  }

  function setMobilePane(pane) {
    if (!["map", "list", "detail"].includes(pane)) return;
    state.mobilePane = pane;
    document.body.classList.remove("mobile-pane-map", "mobile-pane-list", "mobile-pane-detail");
    document.body.classList.add(`mobile-pane-${pane}`);
    document.querySelectorAll(".mobile-tab-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.pane === pane);
    });
    if (pane === "map" && state.pendingMapFit) {
      requestAnimationFrame(() => fitMapToViewport());
    }
  }

  function updateMobileQuickCard() {
    const card = $("mobileQuickCard");
    if (!card) return;
    if (!isCompactDetailLayout()) {
      state.hoveredItemId = null;
      card.classList.add("hidden");
      card.classList.remove("dock-top", "is-hover-preview");
      return;
    }
    const targetId = state.hoveredItemId || state.selectedItemId;
    const it = targetId
      ? state.catalog?.collectibles?.find((x) => x.id === targetId)
      : null;
    if (!it || state.viewMode !== "place" || state.drawerOpen) {
      card.classList.add("hidden");
      card.classList.remove("dock-top", "is-hover-preview");
      return;
    }
    const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
    const cat = getCategoryByKey(it.cat);
    const done = isCollected(it.id);
    const icoEl = $("mqCatIcon");
    if (icoEl) {
      icoEl.style.color = meta.color;
      icoEl.innerHTML = meta.svg;
    }
    if ($("mqTitle")) $("mqTitle").textContent = locText(it.title);
    if ($("mqMeta")) {
      const statusText = done ? t("collected") : t("uncollected");
      const ageLabel = it.age === "child" ? t("ageChild") : it.age === "adult" ? t("ageAdult") : t("ageBoth");
      const nightPart = it.night ? ` · ${t("nightOnly")}` : "";
      $("mqMeta").textContent = `${cat ? locText(cat.name) : it.cat} · ${statusText} · ${ageLabel}${nightPart}`;
    }
    const reqsEl = $("mqReqs");
    const hasReqs = reqsEl ? renderReqChips(reqsEl, it, false) : false;
    reqsEl?.classList.toggle("hidden", !hasReqs);

    const guideEl = $("mqGuideBody");
    if (guideEl) {
      if (guideEl.dataset.itemId !== it.id) {
        guideEl.dataset.itemId = it.id;
        guideEl.scrollTop = 0;
      }
      guideEl.textContent = locText(it.guide) || locText(it.hint) || "";
    }

    card.classList.toggle("dock-top", state.quickCardDock === "top");
    card.classList.toggle("is-hover-preview", Boolean(state.hoveredItemId && state.hoveredItemId !== state.selectedItemId));
    card.classList.remove("hidden");
  }

  function fitMapToViewport() {
    const vp = $("mapViewport");
    const vw = vp.clientWidth;
    const vh = vp.clientHeight;
    if (!vw || !vh) {
      state.pendingMapFit = true;
      return;
    }
    state.pendingMapFit = false;
    const bw = state.mapBaseW || 1000;
    const bh = state.mapBaseH || 700;
    const fitScale = Math.min(vw / bw, vh / bh) * 0.94;
    state.minScale = Math.max(0.08, fitScale * 0.65);
    state.maxScale = bw >= 4000 ? 1.8 : 6.0;
    state.scale = Math.max(state.minScale, Math.min(state.maxScale, fitScale));
    state.tx = (vw - bw * state.scale) / 2;
    state.ty = (vh - bh * state.scale) / 2;
    applyMapTransform();
  }

  function zoomAt(factor, clientX, clientY) {
    const vp = $("mapViewport");
    const rect = vp.getBoundingClientRect();
    const px = clientX !== undefined ? clientX - rect.left : rect.width / 2;
    const py = clientY !== undefined ? clientY - rect.top : rect.height / 2;

    const minS = state.minScale || 0.1;
    const maxS = state.maxScale || 4.0;
    const newScale = Math.max(minS, Math.min(maxS, state.scale * factor));
    const ratio = newScale / state.scale;
    state.tx = px - (px - state.tx) * ratio;
    state.ty = py - (py - state.ty) * ratio;
    state.scale = newScale;
    applyMapTransform();
  }

  function centerOnNormalized(u, v) {
    const vp = $("mapViewport");
    const vw = vp.clientWidth || 800;
    const vh = vp.clientHeight || 600;
    const x = u * state.mapBaseW;
    const y = v * state.mapBaseH;
    state.tx = vw / 2 - x * state.scale;
    state.ty = vh / 2 - y * state.scale;
    applyMapTransform();
  }

  function showMapLoading(label = "") {
    const overlay = $("mapLoadingOverlay");
    const textEl = $("mapLoadingText");
    if (textEl) {
      const msg = {
        "zh-CN": label ? `正在加载「${label}」...` : "正在加载地图数据...",
        "ja": label ? `「${label}」を読み込み中...` : "マップデータを読み込み中...",
        "en": label ? `Loading ${label}...` : "Loading map data...",
      }[state.lang] || (label ? `Loading ${label}...` : "Loading map data...");
      textEl.textContent = msg;
    }
    overlay?.classList.remove("hidden");
  }

  function hideMapLoading() {
    $("mapLoadingOverlay")?.classList.add("hidden");
  }

  function loadMapImageWithOverlay(img, inner, src, label) {
    if (img.dataset.loadedSrc === src && img.complete && img.naturalWidth > 0) {
      inner.classList.remove("is-loading");
      hideMapLoading();
      return;
    }
    const token = ++state.mapLoadToken;
    img.dataset.srcKey = src;
    img.dataset.loadedSrc = "";
    inner.classList.add("is-loading");
    showMapLoading(label);

    const finish = () => {
      if (token !== state.mapLoadToken) return;
      img.onload = null;
      img.onerror = null;
      img.dataset.loadedSrc = src;
      inner.classList.remove("is-loading");
      hideMapLoading();
    };
    img.onload = () => {
      if (typeof img.decode === "function") {
        img.decode().catch(() => {}).finally(finish);
      } else {
        finish();
      }
    };
    img.onerror = finish;
    img.src = src;
    if (img.complete && img.naturalWidth > 0) {
      finish();
    }
  }

  function renderMap() {
    if (!state.catalog) return;
    const img = $("mapImage");
    const inner = $("mapCanvasInner");
    const pinsLayer = $("pinsLayer");
    const floorTabs = $("floorTabs");
    const noMap = $("noMapNotice");
    const crumbWrap = $("crumbPlaceWrap");

    $("btnOverworld").classList.toggle("active", state.viewMode === "overworld");
    inner.classList.toggle("is-overworld", state.viewMode === "overworld");
    updateEraSwitchUi();
    pinsLayer.innerHTML = "";
    floorTabs.innerHTML = "";
    floorTabs.classList.add("hidden");

    const filteredIds = new Set(getFilteredItems().map((it) => it.id));
    const player = getCurrentPlayer();

    if (state.viewMode === "overworld") {
      crumbWrap.classList.add("hidden");
      noMap.classList.add("hidden");
      img.classList.remove("hidden");

      const owSrc = resolveImageUrl(state.catalog.map.image);
      const needFit = img.dataset.srcKey !== owSrc;
      loadMapImageWithOverlay(img, inner, owSrc, t("navOverworld"));
      if (needFit) {
        state.mapBaseW = 6000;
        state.mapBaseH = Math.round(6000 / (state.catalog.map.aspect || 1.3749));
        fitMapToViewport();
      } else {
        applyMapTransform();
      }

      // Render 32 place pins with per-category progress underneath, filtered by active era
      const activeEra = state.overworldEra || "all";
      for (const p of state.catalog.places) {
        if (!p.pin) continue;
        const allItems = state.catalog.collectibles.filter((it) => it.place === p.id && matchesEra(it, activeEra));
        const done = allItems.filter((it) => isCollected(it.id)).length;
        const allComplete = allItems.length > 0 && done === allItems.length;
        const isLinkHere = player?.place === p.id;
        const eraInactive = allItems.length === 0;

        const pin = document.createElement("div");
        pin.className =
          "map-pin place-pin" +
          (p.kind === "dungeon" ? " dungeon" : "") +
          (allComplete ? " complete" : "") +
          (isLinkHere ? " has-link" : "") +
          (eraInactive ? " era-inactive" : "");
        pin.style.left = `${p.pin.x * 100}%`;
        pin.style.top = `${p.pin.y * 100}%`;

        let catsHtml = "";
        if (allItems.length > 0) {
          const parts = [];
          for (const cat of state.catalog.categories) {
            const catItems = allItems.filter((it) => it.cat === cat.key);
            if (!catItems.length) continue;
            const catDone = catItems.filter((it) => isCollected(it.id)).length;
            const meta = CAT_META[cat.key] || { color: "#94a3b8", svg: "•" };
            const isCatDone = catDone === catItems.length;
            const isMatch = state.activeCategoryFilter === cat.key;
            parts.push(
              `<span class="pp-cat${isCatDone ? " cat-done" : ""}${isMatch ? " cat-match" : ""}">` +
                `<span class="pp-ico" style="color:${meta.color}">${meta.svg}</span>` +
                `<b class="pp-val">${catDone}</b><small class="pp-tot">/${catItems.length}</small>` +
              `</span>`
            );
          }
          if (parts.length) {
            catsHtml = `<div class="place-cats-pill">${parts.join("")}</div>`;
          }
        }

        pin.innerHTML =
          `<div class="place-banner"><span>${locText(p.name)}</span>${allComplete ? '<span class="place-done-mark">✓</span>' : ""}</div>` +
          catsHtml;

        pin.addEventListener("click", (e) => {
          if (state.dragMoved) return;
          e.stopPropagation();
          openPlace(p.id, null);
        });
        pinsLayer.appendChild(pin);
      }

      // Render Link marker on overworld without blocking banners
      const owPos = player?.projected?.overworld;
      updateLinkMarker(owPos, player?.rot || 0, "", false, true, false, player?.scene || null);
      return;
    }

    // Place mode
    const place = getPlaceById(state.activePlaceId);
    if (!place) return;
    crumbWrap.classList.remove("hidden");
    $("crumbPlaceName").textContent = locText(place.name);

    const maps = place.maps || [];
    if (!maps.length) {
      state.mapLoadToken++;
      inner.classList.remove("is-loading");
      hideMapLoading();
      img.classList.add("hidden");
      noMap.classList.remove("hidden");
      updateLinkMarker(null, 0, "", false, false);
      return;
    }
    noMap.classList.add("hidden");
    img.classList.remove("hidden");

    if (!state.activeFloorId || !maps.some((m) => m.id === state.activeFloorId)) {
      state.activeFloorId = place.startMap || maps[0].id;
    }

    if (maps.length > 1) {
      floorTabs.classList.remove("hidden");
      for (const m of maps) {
        const btn = document.createElement("button");
        const linkHere = player?.place === place.id && player?.floor === m.id;
        btn.className = "floor-tab" + (m.id === state.activeFloorId ? " active" : "") + (linkHere ? " link-here" : "");
        btn.textContent = locText(m.label);
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          state.activeFloorId = m.id;
          renderMap();
        });
        floorTabs.appendChild(btn);
      }
    }

    const activeMap = maps.find((m) => m.id === state.activeFloorId) || maps[0];
    const mapSrc = resolveImageUrl(activeMap.image);
    const needFit = img.dataset.srcKey !== mapSrc;
    const floorLbl = maps.length > 1 ? `${locText(place.name)} · ${locText(activeMap.label)}` : locText(place.name);
    loadMapImageWithOverlay(img, inner, mapSrc, floorLbl);
    if (needFit) {
      const asp = activeMap.aspect || 1.2;
      state.mapBaseW = 1000;
      state.mapBaseH = Math.round(1000 / asp);
      fitMapToViewport();
    } else {
      applyMapTransform();
    }

    // Render area exit markers on this floor
    const exitsOnFloor = (place.exits || []).filter((ex) => !ex.map || ex.map === activeMap.id);
    for (const ex of exitsOnFloor) {
      const destPlace = ex.to ? getPlaceById(ex.to) : null;
      const exitTitle = ex.label ? locText(ex.label) : destPlace ? locText(destPlace.name) : "";
      const dir = ex.dir || "top";
      const exEl = document.createElement("div");
      exEl.className = `map-pin map-exit dir-${dir}`;
      exEl.style.left = `${ex.x * 100}%`;
      exEl.style.top = `${ex.y * 100}%`;
      if (destPlace) {
        exEl.title = exitTitle;
        exEl.addEventListener("click", (e) => {
          if (state.dragMoved) return;
          e.stopPropagation();
          openPlace(destPlace.id);
        });
      }

      const arrowImg = document.createElement("img");
      arrowImg.className = "exit-arrow-img";
      arrowImg.src = resolveImageUrl(ex.icon || "maps/map_icon_exit.webp");
      arrowImg.alt = "";
      arrowImg.draggable = false;
      arrowImg.style.transform = `rotate(${ex.rot || 0}deg)`;
      exEl.appendChild(arrowImg);

      if (exitTitle) {
        const nameSpan = document.createElement("span");
        nameSpan.className = "exit-name";
        nameSpan.textContent = exitTitle;
        exEl.appendChild(nameSpan);
      }
      pinsLayer.appendChild(exEl);
    }

    // Render collectible pins on this floor
    const itemsOnFloor = state.catalog.collectibles.filter(
      (it) => it.place === place.id && it.at && it.at.map === activeMap.id && filteredIds.has(it.id)
    );
    for (const it of itemsOnFloor) {
      const done = isCollected(it.id);
      const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
      const pin = document.createElement("div");
      pin.className = "map-pin item-pin" + (done ? " collected" : "") + (state.selectedItemId === it.id ? " selected" : "");
      pin.style.left = `${it.at.x * 100}%`;
      pin.style.top = `${it.at.y * 100}%`;
      pin.style.background = meta.color;
      pin.innerHTML = meta.svg;

      pin.addEventListener("mouseenter", (e) => {
        if (isCompactDetailLayout()) {
          if (state.hoverCardTimer) {
            clearTimeout(state.hoverCardTimer);
            state.hoverCardTimer = null;
          }
          state.hoveredItemId = it.id;
          state.quickCardDock = pickNonBlockingDock(pin, it);
          hideTooltip();
          updateMobileQuickCard();
          return;
        }
        showTooltip(e, it);
      });
      pin.addEventListener("mousemove", (e) => {
        if (!isCompactDetailLayout()) moveTooltip(e);
      });
      pin.addEventListener("mouseleave", () => {
        hideTooltip();
        if (isCompactDetailLayout()) {
          if (state.hoverCardTimer) clearTimeout(state.hoverCardTimer);
          state.hoverCardTimer = setTimeout(() => {
            state.hoverCardTimer = null;
            state.hoveredItemId = null;
            updateMobileQuickCard();
          }, 180);
        }
      });
      pin.addEventListener("click", (e) => {
        if (state.dragMoved) return;
        e.stopPropagation();
        if (isCompactDetailLayout()) {
          if (state.hoverCardTimer) {
            clearTimeout(state.hoverCardTimer);
            state.hoverCardTimer = null;
          }
          state.hoveredItemId = null;
          state.quickCardDock = pickNonBlockingDock(pin, it);
        }
        selectItem(it.id, false);
      });
      pinsLayer.appendChild(pin);
    }

    // Render Link marker if in this place
    if (player && player.place === place.id) {
      const pUv = player.projected?.place?.[activeMap.id] || player.projected?.active_place_uv;
      const flMatch = player.floor === activeMap.id;
      const flObj = maps.find((m) => m.id === player.floor);
      const lbl = flMatch ? "" : `${flObj ? locText(flObj.label) : player.floor}`;
      updateLinkMarker(pUv, player.rot || 0, lbl, !flMatch, false, false, player?.scene || null);
    } else {
      updateLinkMarker(null, 0, "", false, false);
    }
  }

  function updateLinkMarker(uv, rotDeg, label, dimmed = false, isOverworld = false, smooth = false, scene = null) {
    const marker = $("linkMarker");
    state.lastLinkOverworldUv = isOverworld ? uv : null;
    if (!uv) {
      marker.classList.add("hidden");
      marker.classList.remove("above-banner", "on-overworld", "live-smooth");
      state.linkArrowDeg = null;
      state.lastLinkMapKey = null;
      state.lastLinkUv = null;
      state.lastLinkScene = null;
      return;
    }
    const mapKey = isOverworld ? "overworld" : `${state.activePlaceId || ""}:${state.activeFloorId || ""}`;
    const isLoadingMap = Boolean($("mapCanvasInner")?.classList.contains("is-loading"));
    const prevUv = state.lastLinkUv;
    const jumpDist = prevUv ? Math.hypot(uv.x - prevUv.x, uv.y - prevUv.y) : Infinity;
    const sceneSame = !scene || !state.lastLinkScene || state.lastLinkScene === scene;
    const useSmooth = Boolean(
      smooth &&
        !isLoadingMap &&
        !marker.classList.contains("hidden") &&
        state.lastLinkMapKey === mapKey &&
        sceneSame &&
        jumpDist <= 0.08
    );
    state.lastLinkMapKey = mapKey;
    state.lastLinkUv = { x: uv.x, y: uv.y };
    state.lastLinkScene = scene || null;
    marker.classList.toggle("live-smooth", useSmooth);
    marker.classList.remove("hidden");
    marker.classList.toggle("on-overworld", Boolean(isOverworld));
    marker.style.left = `${uv.x * 100}%`;
    marker.style.top = `${uv.y * 100}%`;
    marker.style.opacity = dimmed ? "0.55" : "1";

    const targetDeg = Number.isFinite(rotDeg) ? rotDeg : 0;
    if (!useSmooth || state.linkArrowDeg === null) {
      state.linkArrowDeg = targetDeg;
    } else {
      const delta = ((((targetDeg - state.linkArrowDeg) % 360) + 540) % 360) - 180;
      state.linkArrowDeg += delta;
    }
    $("linkArrow").style.transform = `rotate(${state.linkArrowDeg}deg)`;

    const lblEl = $("linkLabel");
    if (label && !isOverworld) {
      lblEl.textContent = label;
      lblEl.classList.remove("hidden");
    } else {
      lblEl.classList.add("hidden");
    }
    refreshLinkOverlapClass();
    if (!useSmooth) {
      void marker.offsetWidth;
    }
  }

  function showTooltip(e, it) {
    const tip = $("hoverTooltip");
    const cat = getCategoryByKey(it.cat);
    const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
    const done = isCollected(it.id);
    tip.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;font-weight:700;margin-bottom:2px;color:#f4dc94;">
        <span class="cat-svg" style="color:${meta.color}">${meta.svg}</span>
        <span>${locText(it.title)}</span>
      </div>
      <div style="color:#b6a88d;font-size:11px;">${cat ? locText(cat.name) : it.cat} · ${done ? t("collected") : t("uncollected")}</div>
    `;
    tip.classList.remove("hidden");
    moveTooltip(e);
  }

  function moveTooltip(e) {
    const tip = $("hoverTooltip");
    tip.style.left = `${Math.min(window.innerWidth - 270, e.clientX + 14)}px`;
    tip.style.top = `${Math.min(window.innerHeight - 80, e.clientY + 14)}px`;
  }

  function hideTooltip() {
    $("hoverTooltip").classList.add("hidden");
  }

  function renderDetailPanel() {
    if (!state.catalog) return;
    if (!state.selectedItemId) {
      $("detailItem").classList.add("hidden");
      $("detailEmpty").classList.remove("hidden");
      renderPlaceOverview();
      return;
    }

    const it = state.catalog.collectibles.find((x) => x.id === state.selectedItemId);
    if (!it) return;

    $("detailEmpty").classList.add("hidden");
    $("detailItem").classList.remove("hidden");

    const cat = getCategoryByKey(it.cat);
    const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
    const place = getPlaceById(it.place);
    const savedDone = isSavedCollected(it.id);
    const effectiveDone = isCollected(it.id);

    const catBadge = $("detailCatBadge");
    catBadge.innerHTML = `<span class="cat-svg">${meta.svg}</span><span>${cat ? locText(cat.name) : it.cat}</span>`;
    catBadge.style.background = meta.color;

    const verBadge = $("detailVerifyBadge");
    verBadge.className = "verify-badge " + (savedDone ? "done" : "todo");
    verBadge.textContent = savedDone ? t("savedInFile") : t("notInSave");

    $("detailTitle").textContent = locText(it.title);
    const floorObj = place?.maps?.find((m) => m.id === it.at?.map);
    $("detailPlaceMeta").textContent = `${place ? locText(place.name) : it.place}${floorObj ? " · " + locText(floorObj.label) : ""} (#${it.n})`;

    // Tags (Age & Day/Night)
    const tagsEl = $("detailTags");
    tagsEl.innerHTML = "";
    const ageLabel = it.age === "child" ? t("ageChild") : it.age === "adult" ? t("ageAdult") : t("ageBoth");
    const ageTag = document.createElement("span");
    ageTag.className = "dtag";
    ageTag.textContent = ageLabel;
    tagsEl.appendChild(ageTag);

    const nightTag = document.createElement("span");
    nightTag.className = "dtag" + (it.night ? " night" : "");
    nightTag.textContent = it.night ? t("nightOnly") : t("dayOrNight");
    tagsEl.appendChild(nightTag);

    // Requirements
    renderReqChips($("detailReqs"), it, true);

    // Guide
    $("detailGuide").textContent = locText(it.guide);

    // Coords & Flag
    $("detailCoords").textContent = it.coords ? it.coords.map((v) => v.toFixed(1)).join(", ") : "-";
    const r = it.rule;
    if (r?.type === "b64") {
      $("detailFlag").textContent = `Bool64 0x${BigInt(r.hash).toString(16)}`;
    } else if (r?.type === "bool32") {
      $("detailFlag").textContent = r.flag;
    } else if (r?.type === "bool32_any") {
      $("detailFlag").textContent = r.flags.join(" | ");
    } else if (r?.type === "int_gte") {
      $("detailFlag").textContent = `${r.flag} >= ${r.target}`;
    } else {
      $("detailFlag").textContent = "-";
    }

    $("chkManualOverride").checked = effectiveDone;
    $("txtItemNote").value = state.serverState?.overrides?.notes?.[it.id] || "";
  }

  function renderPlaceOverview() {
    if (!state.catalog) return;
    const el = $("placeOverview");
    el.innerHTML = "";
    const place = state.viewMode === "place" ? getPlaceById(state.activePlaceId) : null;

    if (!place) {
      const h2 = document.createElement("h2");
      h2.textContent = t("navOverworld");
      const p = document.createElement("p");
      p.textContent = t("memoryScanHint");
      el.appendChild(h2);
      el.appendChild(p);
      return;
    }

    const items = state.catalog.collectibles.filter(
      (it) => it.place === place.id && matchesEra(it, state.overworldEra)
    );
    const done = items.filter((it) => isCollected(it.id)).length;

    const h2 = document.createElement("h2");
    h2.textContent = `${locText(place.name)} (${done}/${items.length})`;
    const p = document.createElement("p");
    p.textContent = locText(place.intro);
    el.appendChild(h2);
    el.appendChild(p);

    const list = document.createElement("div");
    list.className = "place-items-mini";
    for (const it of items) {
      const cDone = isCollected(it.id);
      const meta = CAT_META[it.cat] || { color: "#94a3b8", svg: "•" };
      const row = document.createElement("div");
      row.className = "item-row" + (cDone ? " collected" : "");
      row.innerHTML = `
        <div class="item-row-left">
          <span class="cat-svg" style="color:${meta.color}">${meta.svg}</span>
          <span class="item-row-title">${locText(it.title)}</span>
        </div>
        <span class="badge-count ${cDone ? "complete" : ""}">${cDone ? "✓" : "•"}</span>
      `;
      row.addEventListener("click", () => selectItem(it.id, true));
      list.appendChild(row);
    }
    el.appendChild(list);
  }

  function openPlace(placeId, floorId = null, keepItem = false) {
    if (state.hoverCardTimer) {
      clearTimeout(state.hoverCardTimer);
      state.hoverCardTimer = null;
    }
    state.hoveredItemId = null;
    state.viewMode = "place";
    state.activePlaceId = placeId;
    const place = getPlaceById(placeId);
    let pickedFloor = floorId;
    if (!pickedFloor && place?.maps?.length) {
      if (state.overworldEra === "child" && place.maps.some((m) => m.id === "nino")) {
        pickedFloor = "nino";
      } else if (state.overworldEra === "adult" && place.maps.some((m) => m.id === "adulto")) {
        pickedFloor = "adulto";
      } else {
        pickedFloor = place.startMap || place.maps[0].id;
      }
    }
    state.activeFloorId = pickedFloor || null;
    if (!keepItem) state.selectedItemId = null;
    if (isMobileLayout()) setMobilePane("map");
    renderAllListsAndMap();
  }

  function openOverworld() {
    if (state.hoverCardTimer) {
      clearTimeout(state.hoverCardTimer);
      state.hoverCardTimer = null;
    }
    state.hoveredItemId = null;
    state.viewMode = "overworld";
    state.activePlaceId = null;
    state.activeFloorId = null;
    if (isMobileLayout()) setMobilePane("map");
    renderAllListsAndMap();
  }

  function setOverworldEra(era) {
    if (!["child", "adult", "all"].includes(era)) return;
    state.overworldEra = era;
    state.filterAge = era;
    $("filterAge").value = era;
    if (state.viewMode === "place" && state.activePlaceId) {
      const place = getPlaceById(state.activePlaceId);
      if (era === "child" && place?.maps?.some((m) => m.id === "nino")) {
        state.activeFloorId = "nino";
      } else if (era === "adult" && place?.maps?.some((m) => m.id === "adulto")) {
        state.activeFloorId = "adulto";
      }
    }
    renderAllListsAndMap();
  }

  function selectItem(itemId, jumpToMap = true) {
    const it = state.catalog?.collectibles?.find((x) => x.id === itemId);
    if (!it) return;
    state.selectedItemId = itemId;
    if (jumpToMap) {
      state.viewMode = "place";
      state.activePlaceId = it.place;
      if (it.at?.map) state.activeFloorId = it.at.map;
      if (isMobileLayout()) setMobilePane("map");
    }
    renderAllListsAndMap();
    if (jumpToMap && it.at) {
      setTimeout(() => {
        centerOnNormalized(it.at.x, it.at.y);
        if (isCompactDetailLayout()) {
          state.quickCardDock = pickNonBlockingDock(null, it);
          updateMobileQuickCard();
        }
      }, 40);
    }
  }

  function renderAllListsAndMap() {
    renderHeaderSyncAndTelemetry();
    renderCategories();
    renderNavLists();
    renderMap();
    renderDetailPanel();
    updateMobileQuickCard();
  }

  function applyAutoFollowMap(player, renderNow = true) {
    if (!player) return;
    const detectedEra = detectPlayerEra(player);
    if (detectedEra && detectedEra !== state.overworldEra) {
      state.overworldEra = detectedEra;
      state.filterAge = detectedEra;
      $("filterAge").value = detectedEra;
    }
    const pl = getPlaceById(player.place);
    if (renderNow) {
      if (pl && pl.maps && pl.maps.length) {
        openPlace(pl.id, player.floor, true);
      } else {
        openOverworld();
      }
    } else if (pl && pl.maps && pl.maps.length) {
      state.viewMode = "place";
      state.activePlaceId = pl.id;
      state.activeFloorId = player.floor || pl.startMap || pl.maps[0].id;
    } else {
      state.viewMode = "overworld";
      state.activePlaceId = null;
      state.activeFloorId = null;
    }
  }

  function handleServerState(newState, isInitial = false) {
    state.serverState = newState;
    if (isInitial && newState.config?.language && ["zh-CN", "ja", "en"].includes(newState.config.language)) {
      state.lang = newState.config.language;
      applyStaticI18n();
    }

    const player = getCurrentPlayer(newState);
    const lpKey = player ? `${player.place || ""}:${player.floor || ""}` : null;

    if (isInitial) {
      state.viewMode = "overworld";
      state.activePlaceId = null;
      state.activeFloorId = null;
      const detectedEra = detectPlayerEra(player) || "child";
      state.overworldEra = detectedEra;
      state.filterAge = detectedEra;
      $("filterAge").value = detectedEra;
      $("chkAutoMap").checked = state.autoFollowMap;
      if (player) state.lastLinkPlaceFloor = lpKey;
      if (state.autoFollowMap && player) {
        applyAutoFollowMap(player, false);
      }
    } else if (state.autoFollowMap && player && lpKey && lpKey !== state.lastLinkPlaceFloor) {
      state.lastLinkPlaceFloor = lpKey;
      applyAutoFollowMap(player, false);
    } else if (player) {
      state.lastLinkPlaceFloor = lpKey;
    }

    renderSaveSlotsAndPouch();
    renderAllListsAndMap();
  }

  function handlePlayerUpdate(msg) {
    if (!state.serverState) return;
    const player = msg.player || null;
    state.serverState.sync = msg.sync || state.serverState.sync;
    state.serverState.live_player = player;
    if (state.serverState.save) {
      state.serverState.save.player = player;
    }

    renderHeaderSyncAndTelemetry();

    const lpKey = player ? `${player.place || ""}:${player.floor || ""}` : null;
    if (lpKey !== state.lastLinkPlaceFloor) {
      state.lastLinkPlaceFloor = lpKey;
      if (state.autoFollowMap && player && lpKey) {
        applyAutoFollowMap(player, true);
        return;
      }
      renderNavLists();
      renderMap();
      return;
    }

    if (!player) {
      updateLinkMarker(null, 0, "", false, false, false);
      return;
    }

    if (state.viewMode === "overworld") {
      const owPos = player.projected?.overworld || null;
      updateLinkMarker(owPos, player.rot || 0, "", false, true, true, player?.scene || null);
    } else if (state.viewMode === "place") {
      const place = getPlaceById(state.activePlaceId);
      if (place && player.place === place.id) {
        const maps = place.maps || [];
        const activeMap = maps.find((m) => m.id === state.activeFloorId) || maps[0];
        if (activeMap) {
          const pUv = player.projected?.place?.[activeMap.id] || player.projected?.active_place_uv || null;
          const flMatch = player.floor === activeMap.id;
          const flObj = maps.find((m) => m.id === player.floor);
          const lbl = flMatch ? "" : `${flObj ? locText(flObj.label) : player.floor}`;
          updateLinkMarker(pUv, player.rot || 0, lbl, !flMatch, false, true, player?.scene || null);
        } else {
          updateLinkMarker(null, 0, "", false, false, false);
        }
      } else {
        updateLinkMarker(null, 0, "", false, false, false);
      }
    }
  }

  async function selectSlot(profile, slot) {
    if (state.staticMode) {
      const entry = webSync.slotCache.get(`${profile}/${slot}`);
      if (!entry) return;
      state.serverState.config.profile = profile;
      state.serverState.config.slot = slot;
      state.serverState.config.auto_follow_slot = false;
      state.serverState.save = entry.parsed;
      webSync.lastSignature = "";
      writeLocalJson(WEB_STORAGE_KEYS.save, entry.parsed);
      handleServerState(state.serverState, false);
      return;
    }
    state.serverState = await fetchJson("/api/saves/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile, slot, auto_follow_slot: false }),
    });
    handleServerState(state.serverState, false);
  }

  async function fetchJson(url, opts) {
    const target = url.startsWith("/api/") ? `${state.apiBase}${url}` : url;
    const res = await fetch(target, opts);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  }

  function connectWebSocket() {
    let wsUrl;
    if (state.apiBase) {
      wsUrl = state.apiBase.replace(/^http/, "ws") + "/api/ws";
    } else {
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${proto}//${location.host}/api/ws`;
    }
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.ping) return;
        if (msg.type === "player") {
          handlePlayerUpdate(msg);
          return;
        }
        handleServerState(msg, false);
      } catch (err) {
        console.error(err);
      }
    };
    ws.onclose = () => {
      if (!state.staticMode) setTimeout(connectWebSocket, 2000);
    };
  }

  // Directory browser modal
  async function loadBrowseDir(path) {
    const url = path ? `/api/browse-dir?path=${encodeURIComponent(path)}` : "/api/browse-dir";
    const data = await fetchJson(url);
    state.browsePath = data.path || "";
    $("browsePathInput").value = state.browsePath;

    const drivesEl = $("browseDrives");
    drivesEl.innerHTML = "";
    for (const d of data.drives || []) {
      const b = document.createElement("button");
      b.className = "btn-sm";
      b.textContent = d;
      b.addEventListener("click", () => loadBrowseDir(d));
      drivesEl.appendChild(b);
    }

    $("btnBrowseUp").disabled = !data.parent;
    $("btnBrowseUp").onclick = () => data.parent && loadBrowseDir(data.parent);

    const listEl = $("browseDirsList");
    listEl.innerHTML = "";
    for (const d of data.dirs || []) {
      const row = document.createElement("div");
      row.className = "dir-row";
      const tag = d.has_sav ? "progress.sav" : d.has_slots ? "slot_*" : "";
      row.innerHTML = `<span>📁 ${d.name}</span>${tag ? `<span class="dir-tag">${tag}</span>` : ""}`;
      row.addEventListener("click", () => loadBrowseDir(d.path));
      listEl.appendChild(row);
    }
  }

  function bindEvents() {
    // Language buttons
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        state.lang = btn.dataset.lang;
        applyStaticI18n();
        renderSaveSlotsAndPouch();
        renderAllListsAndMap();
        if (state.staticMode) {
          writeLocalJson(WEB_STORAGE_KEYS.lang, state.lang);
          return;
        }
        await fetchJson("/api/language", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ language: state.lang }),
        });
      });
    });

    // Overworld era buttons (Child / Adult / All)
    document.querySelectorAll(".era-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        setOverworldEra(btn.dataset.era);
      });
    });

    // Save controls
    $("btnRescan").addEventListener("click", async () => {
      const p = $("inputSavePath").value.trim();
      const s = await fetchJson("/api/saves/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ save_root: p }),
      });
      handleServerState(s, false);
    });
    $("inputSavePath").addEventListener("keydown", (e) => {
      if (e.key === "Enter") $("btnRescan").click();
    });
    $("chkAutoSlot").addEventListener("change", async (e) => {
      if (state.staticMode) {
        state.serverState.config.auto_follow_slot = e.target.checked;
        if (e.target.checked && webSync.slotCache.size) {
          const profiles = state.serverState.discovery?.profiles || [];
          const parsedMap = new Map();
          for (const [k, v] of webSync.slotCache.entries()) parsedMap.set(k, v.parsed);
          webSync.lastSignature = "";
          applyWebDiscoveredProfiles(profiles, parsedMap, Boolean(webSync.dirHandle), webSync.dirName);
        }
        return;
      }
      const s = await fetchJson("/api/saves/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auto_follow_slot: e.target.checked }),
      });
      handleServerState(s, false);
    });
    $("chkAutoMap").addEventListener("change", (e) => {
      state.autoFollowMap = e.target.checked;
      const player = getCurrentPlayer();
      if (state.autoFollowMap && player) {
        applyAutoFollowMap(player, true);
      }
    });

    // Directory browser modal
    $("btnBrowseDir").addEventListener("click", () => {
      $("browseModal").classList.remove("hidden");
      loadBrowseDir($("inputSavePath").value.trim());
    });
    $("btnBrowseClose").addEventListener("click", () => $("browseModal").classList.add("hidden"));
    $("btnBrowseCancel").addEventListener("click", () => $("browseModal").classList.add("hidden"));
    $("btnBrowseGo").addEventListener("click", () => loadBrowseDir($("browsePathInput").value.trim()));
    $("btnBrowseSelect").addEventListener("click", async () => {
      $("browseModal").classList.add("hidden");
      $("inputSavePath").value = state.browsePath;
      $("btnRescan").click();
    });

    // Nav tabs & filters
    $("tabPlaces").addEventListener("click", () => {
      state.navTab = "places";
      $("tabPlaces").classList.add("active");
      $("tabItems").classList.remove("active");
      $("placesList").classList.remove("hidden");
      $("itemsList").classList.add("hidden");
    });
    $("tabItems").addEventListener("click", () => {
      state.navTab = "items";
      $("tabItems").classList.add("active");
      $("tabPlaces").classList.remove("active");
      $("itemsList").classList.remove("hidden");
      $("placesList").classList.add("hidden");
    });
    $("searchInput").addEventListener("input", (e) => {
      state.search = e.target.value;
      renderNavLists();
      renderMap();
    });
    $("filterStatus").addEventListener("change", (e) => {
      state.filterStatus = e.target.value;
      renderNavLists();
      renderMap();
    });
    $("filterAge").addEventListener("change", (e) => {
      state.filterAge = e.target.value;
      if (["child", "adult", "all"].includes(state.filterAge)) {
        state.overworldEra = state.filterAge;
      }
      renderAllListsAndMap();
    });

    // Map toolbar
    $("btnToggleLabels").addEventListener("click", () => {
      state.showLabels = !state.showLabels;
      $("btnToggleLabels").classList.toggle("active", state.showLabels);
      $("mapViewport").classList.toggle("labels-hidden", !state.showLabels);
    });
    $("btnOverworld").addEventListener("click", openOverworld);
    $("btnBackToOverworld").addEventListener("click", openOverworld);
    $("btnZoomIn").addEventListener("click", () => zoomAt(1.25));
    $("btnZoomOut").addEventListener("click", () => zoomAt(0.8));
    $("btnResetZoom").addEventListener("click", fitMapToViewport);
    $("btnCenterLink").addEventListener("click", () => {
      const player = getCurrentPlayer();
      if (!player) return;
      const pl = getPlaceById(player.place);
      if (pl && pl.maps && pl.maps.length && (state.viewMode !== "place" || state.activePlaceId !== pl.id || state.activeFloorId !== player.floor)) {
        openPlace(pl.id, player.floor, true);
        setTimeout(() => {
          const uv = player.projected?.active_place_uv;
          if (uv) centerOnNormalized(uv.x, uv.y);
        }, 40);
        return;
      }
      const uv = state.viewMode === "overworld"
        ? player.projected?.overworld
        : player.projected?.place?.[state.activeFloorId] || player.projected?.active_place_uv;
      if (uv) centerOnNormalized(uv.x, uv.y);
    });

    // Pan & Zoom on viewport (Mouse + Touch Pan & Pinch)
    const vp = $("mapViewport");
    const uiGuardSelector = "#floorTabs, #mobileQuickCard, .no-map-notice";
    vp.addEventListener("wheel", (e) => {
      if (e.target.closest(uiGuardSelector)) return;
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      zoomAt(factor, e.clientX, e.clientY);
    }, { passive: false });
    vp.addEventListener("mousedown", (e) => {
      if (e.button !== 0 || e.target.closest(uiGuardSelector)) return;
      state.dragging = true;
      state.dragMoved = false;
      state.dragStartX = e.clientX;
      state.dragStartY = e.clientY;
      state.dragStartTx = state.tx;
      state.dragStartTy = state.ty;
    });
    window.addEventListener("mousemove", (e) => {
      if (!state.dragging) return;
      const dx = e.clientX - state.dragStartX;
      const dy = e.clientY - state.dragStartY;
      if (Math.hypot(dx, dy) > 4) state.dragMoved = true;
      state.tx = state.dragStartTx + dx;
      state.ty = state.dragStartTy + dy;
      applyMapTransform();
    });
    window.addEventListener("mouseup", () => {
      state.dragging = false;
    });
    vp.addEventListener("click", (e) => {
      if (state.dragMoved) return;
      if (e.target.closest(".map-pin") || e.target.closest(uiGuardSelector)) return;
      if (isCompactDetailLayout() && state.selectedItemId) {
        state.selectedItemId = null;
        state.hoveredItemId = null;
        renderMap();
        renderDetailPanel();
        updateMobileQuickCard();
      }
    });

    let touchMode = null; // null | "pan" | "pinch"
    let pinchStartDist = 1;
    let pinchStartScale = 1;
    let pinchStartMidX = 0;
    let pinchStartMidY = 0;
    let pinchWorldX = 0;
    let pinchWorldY = 0;

    const beginPinch = (t1, t2) => {
      const rect = vp.getBoundingClientRect();
      const mx = (t1.clientX + t2.clientX) / 2 - rect.left;
      const my = (t1.clientY + t2.clientY) / 2 - rect.top;
      touchMode = "pinch";
      state.dragMoved = true;
      pinchStartDist = Math.max(8, Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY));
      pinchStartScale = state.scale;
      pinchStartMidX = mx;
      pinchStartMidY = my;
      pinchWorldX = (mx - state.tx) / pinchStartScale;
      pinchWorldY = (my - state.ty) / pinchStartScale;
    };

    vp.addEventListener("touchstart", (e) => {
      if (e.target.closest(uiGuardSelector)) {
        touchMode = null;
        return;
      }
      if (e.touches.length === 1) {
        touchMode = "pan";
        state.dragMoved = false;
        state.dragStartX = e.touches[0].clientX;
        state.dragStartY = e.touches[0].clientY;
        state.dragStartTx = state.tx;
        state.dragStartTy = state.ty;
      } else if (e.touches.length >= 2) {
        e.preventDefault();
        beginPinch(e.touches[0], e.touches[1]);
      }
    }, { passive: false });

    vp.addEventListener("touchmove", (e) => {
      if (!touchMode) return;
      if (touchMode === "pinch" && e.touches.length >= 2) {
        e.preventDefault();
        const t1 = e.touches[0];
        const t2 = e.touches[1];
        const rect = vp.getBoundingClientRect();
        const mx = (t1.clientX + t2.clientX) / 2 - rect.left;
        const my = (t1.clientY + t2.clientY) / 2 - rect.top;
        const dist = Math.max(8, Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY));
        const minS = state.minScale || 0.1;
        const maxS = state.maxScale || 4.0;
        const nextScale = Math.max(minS, Math.min(maxS, pinchStartScale * (dist / pinchStartDist)));
        state.scale = nextScale;
        state.tx = mx - pinchWorldX * nextScale;
        state.ty = my - pinchWorldY * nextScale;
        applyMapTransform();
      } else if (touchMode === "pan" && e.touches.length === 1) {
        const dx = e.touches[0].clientX - state.dragStartX;
        const dy = e.touches[0].clientY - state.dragStartY;
        if (Math.hypot(dx, dy) > 6) {
          state.dragMoved = true;
          e.preventDefault();
        }
        if (state.dragMoved) {
          state.tx = state.dragStartTx + dx;
          state.ty = state.dragStartTy + dy;
          applyMapTransform();
        }
      }
    }, { passive: false });

    const onTouchEndOrCancel = (e) => {
      if (e.touches.length === 1 && touchMode === "pinch") {
        touchMode = "pan";
        state.dragStartX = e.touches[0].clientX;
        state.dragStartY = e.touches[0].clientY;
        state.dragStartTx = state.tx;
        state.dragStartTy = state.ty;
      } else if (e.touches.length === 0) {
        touchMode = null;
      }
    };
    vp.addEventListener("touchend", onTouchEndOrCancel);
    vp.addEventListener("touchcancel", onTouchEndOrCancel);

    // Manual override & note
    $("chkManualOverride").addEventListener("change", async (e) => {
      if (!state.selectedItemId) return;
      const saved = isSavedCollected(state.selectedItemId);
      const checked = e.target.checked === saved ? null : e.target.checked;
      if (state.staticMode) {
        const ov = state.serverState.overrides || { checks: {}, notes: {} };
        if (checked === null) delete ov.checks[state.selectedItemId];
        else ov.checks[state.selectedItemId] = checked;
        state.serverState.overrides = ov;
        writeLocalJson(WEB_STORAGE_KEYS.overrides, ov);
        renderAllListsAndMap();
        return;
      }
      const res = await fetchJson("/api/manual-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: state.selectedItemId, checked }),
      });
      state.serverState.overrides = res.overrides;
      renderAllListsAndMap();
    });
    let noteTimer = null;
    $("txtItemNote").addEventListener("input", (e) => {
      if (!state.selectedItemId) return;
      const iid = state.selectedItemId;
      const val = e.target.value;
      clearTimeout(noteTimer);
      noteTimer = setTimeout(async () => {
        if (state.staticMode) {
          const ov = state.serverState.overrides || { checks: {}, notes: {} };
          if (val.trim()) ov.notes[iid] = val;
          else delete ov.notes[iid];
          state.serverState.overrides = ov;
          writeLocalJson(WEB_STORAGE_KEYS.overrides, ov);
          return;
        }
        const res = await fetchJson("/api/manual-check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            item_id: iid,
            checked: Object.prototype.hasOwnProperty.call(state.serverState?.overrides?.checks || {}, iid)
              ? state.serverState.overrides.checks[iid]
              : null,
            note: val,
          }),
        });
        state.serverState.overrides = res.overrides;
      }, 400);
    });

    // Web/Vercel local folder live-sync
    $("btnPickWebDir")?.addEventListener("click", async () => {
      if (typeof window.showDirectoryPicker === "function") {
        try {
          const handle = await window.showDirectoryPicker({ id: "oot-save-dir", mode: "read" });
          await startWebDirectorySync(handle);
        } catch (err) {
          if (err?.name !== "AbortError") {
            alert(`Folder access error: ${err.message}`);
          }
        }
      } else {
        $("dirSaveUpload")?.click();
      }
    });
    $("btnResumeWebDir")?.addEventListener("click", async () => {
      const handle = webSync.pendingDirHandle;
      if (!handle) return;
      try {
        const perm = await handle.requestPermission({ mode: "read" });
        if (perm === "granted") {
          await startWebDirectorySync(handle);
        }
      } catch (err) {
        alert(`Permission error: ${err.message}`);
      }
    });
    $("dirSaveUpload")?.addEventListener("change", async (e) => {
      const files = e.target.files;
      await scanWebFileList(files);
      e.target.value = "";
    });
    $("btnClearWebSave")?.addEventListener("click", () => {
      stopWebDirectorySync(true);
      writeLocalJson(WEB_STORAGE_KEYS.save, null);
      state.serverState.save = null;
      state.serverState.discovery = { save_root: "", exists: false, profiles: [] };
      state.serverState.config.profile = null;
      state.serverState.config.slot = null;
      state.serverState.sync = { mode: "web_manual", process_running: false, process_name: null, memory_attached: false };
      handleServerState(state.serverState, false);
    });
    const closeResetModal = () => $("resetChecksModal")?.classList.add("hidden");
    $("btnResetWebChecks")?.addEventListener("click", () => {
      const count = Object.keys(state.serverState?.overrides?.checks || {}).length;
      const desc = {
        "zh-CN":
          `「重置勾选」只会清空你在网页中「手动覆写标记」的收集状态（当前共 ${count} 条）。\n\n` +
          `• 重置后：所有道具恢复为完全以同步的 progress.sav 存档为准（未导入存档则全部未收集）。\n` +
          `• 不会影响：你在道具详情里写的个人备注、已连接的同步文件夹以及电脑本地的游戏存档。\n\n` +
          `确定要重置所有手动勾选吗？`,
        "ja":
          `「手動チェック初期化」は、ブラウザ上で「手動上書きチェック」した記録のみを消去します（現在 ${count} 件）。\n\n` +
          `• 初期化後：すべての収集状態は同期中の progress.sav 準拠に戻ります。\n` +
          `• 影響しないもの：個人メモ、同期中のフォルダ接続、PC内のセーブデータ本体。\n\n` +
          `手動チェックをすべてリセットしますか？`,
        "en":
          `"Reset Checks" clears only your manual check overrides saved in this browser (${count} currently set).\n\n` +
          `• After reset: item status strictly reflects the synced progress.sav (or all uncollected if no save is loaded).\n` +
          `• Preserved: your personal notes, synced save folder connection, and your actual game save files.\n\n` +
          `Are you sure you want to reset all manual check overrides?`,
      }[state.lang] || `Clear ${count} manual check override(s)? Your notes and save files will not be affected.`;
      if ($("lblResetModalDesc")) $("lblResetModalDesc").textContent = desc;
      $("resetChecksModal")?.classList.remove("hidden");
    });
    $("btnResetModalClose")?.addEventListener("click", closeResetModal);
    $("btnResetModalCancel")?.addEventListener("click", closeResetModal);
    $("resetChecksModal")?.addEventListener("click", (e) => {
      if (e.target === $("resetChecksModal")) closeResetModal();
    });
    $("btnResetModalConfirm")?.addEventListener("click", () => {
      const ov = { checks: {}, notes: state.serverState?.overrides?.notes || {} };
      writeLocalJson(WEB_STORAGE_KEYS.overrides, ov);
      state.serverState.overrides = ov;
      closeResetModal();
      renderAllListsAndMap();
    });

    // Tablet detail drawer & Mobile bottom tabs / quick card
    $("btnToggleDetailDrawer")?.addEventListener("click", () => {
      setTabletDrawerOpen(!state.drawerOpen);
    });
    $("btnCloseDetailDrawer")?.addEventListener("click", () => setTabletDrawerOpen(false));
    $("tabletDrawerBackdrop")?.addEventListener("click", () => setTabletDrawerOpen(false));
    document.querySelectorAll(".mobile-tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => setMobilePane(btn.dataset.pane));
    });
    $("btnMqGuide")?.addEventListener("click", () => {
      const targetId = state.hoveredItemId || state.selectedItemId;
      if (targetId && state.selectedItemId !== targetId) {
        state.selectedItemId = targetId;
        state.hoveredItemId = null;
        renderNavLists();
        renderMap();
        renderDetailPanel();
      }
      if (isTabletLayout()) {
        setTabletDrawerOpen(true);
      } else {
        setMobilePane("detail");
      }
    });
    $("btnMqClose")?.addEventListener("click", () => {
      if (state.hoverCardTimer) {
        clearTimeout(state.hoverCardTimer);
        state.hoverCardTimer = null;
      }
      state.hoveredItemId = null;
      state.selectedItemId = null;
      renderNavLists();
      renderMap();
      renderDetailPanel();
      updateMobileQuickCard();
    });
    $("mobileQuickCard")?.addEventListener("mouseenter", () => {
      if (state.hoverCardTimer) {
        clearTimeout(state.hoverCardTimer);
        state.hoverCardTimer = null;
      }
    });
    $("mobileQuickCard")?.addEventListener("mouseleave", () => {
      if (isCompactDetailLayout() && state.hoveredItemId) {
        if (state.hoverCardTimer) clearTimeout(state.hoverCardTimer);
        state.hoverCardTimer = setTimeout(() => {
          state.hoverCardTimer = null;
          state.hoveredItemId = null;
          updateMobileQuickCard();
        }, 180);
      }
    });

    if (typeof ResizeObserver === "function" && $("mapViewport")) {
      const ro = new ResizeObserver(() => {
        if (state.pendingMapFit) fitMapToViewport();
      });
      ro.observe($("mapViewport"));
    }

    window.addEventListener("resize", () => {
      if (!isTabletLayout() && state.drawerOpen) {
        setTabletDrawerOpen(false);
      }
      updateMobileQuickCard();
      fitMapToViewport();
    });
  }

  async function init() {
    const preLang = readLocalJson(WEB_STORAGE_KEYS.lang, "zh-CN");
    if (["zh-CN", "ja", "en"].includes(preLang)) state.lang = preLang;
    setMobilePane("map");
    showMapLoading("");
    bindEvents();
    let cat = null;
    let initial = null;
    try {
      [cat, initial] = await Promise.all([
        fetchJson("/api/catalog"),
        fetchJson("/api/state"),
      ]);
      state.staticMode = false;
      document.body.classList.remove("static-mode");
    } catch {
      state.staticMode = true;
      document.body.classList.add("static-mode");
      cat = await fetchJson("/data/catalog.json");
      const savedLang = readLocalJson(WEB_STORAGE_KEYS.lang, "zh-CN");
      const savedOv = readLocalJson(WEB_STORAGE_KEYS.overrides, { checks: {}, notes: {} });
      const savedData = readLocalJson(WEB_STORAGE_KEYS.save, null);
      initial = {
        config: { language: ["zh-CN", "ja", "en"].includes(savedLang) ? savedLang : "zh-CN", save_root: "", auto_follow_slot: true },
        sync: { mode: savedData ? "web_save" : "web_manual", process_running: false, process_name: null, memory_attached: false },
        discovery: { exists: false, profiles: [] },
        save: savedData,
        overrides: { checks: savedOv.checks || {}, notes: savedOv.notes || {} },
      };
    }

    state.catalog = cat;
    handleServerState(initial, true);
    applyStaticI18n();
    updateEraSwitchUi();
    if (!state.staticMode) {
      connectWebSocket();
    } else {
      const savedDir = await idbGetSavedDirHandle();
      if (savedDir && typeof savedDir.queryPermission === "function") {
        try {
          const perm = await savedDir.queryPermission({ mode: "read" });
          if (perm === "granted") {
            await startWebDirectorySync(savedDir);
          } else if (perm === "prompt") {
            webSync.pendingDirHandle = savedDir;
            renderSaveSlotsAndPouch();
          }
        } catch {
          // ignore stale handle
        }
      }
    }
  }

  init().catch((err) => {
    console.error("Init failed:", err);
    document.querySelector(".map-loading-spinner")?.classList.add("hidden");
    const textEl = $("mapLoadingText");
    if (textEl) textEl.textContent = `加载失败: ${err?.message || err}`;
  });
})();
