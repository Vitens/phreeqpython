(function () {
  let inflight = 0;
  const idleWaiters = [];

  function helpersScript() {
    const scripts = document.querySelectorAll("script[src]");
    for (const script of scripts) {
      if (script.src.includes("pyodide-helpers")) {
        return script;
      }
    }
    return null;
  }

  function helperUrl() {
    const script = helpersScript();
    if (script) {
      return new URL("../pyodide/ppdocs.py", script.src).href;
    }
    return new URL("pyodide/ppdocs.py", document.baseURI).href;
  }

  function rewriteInstallPaths() {
    const script = helpersScript();
    const wheelsBase = script
      ? new URL("../wheels/", script.src)
      : new URL("wheels/", document.baseURI);
    document.querySelectorAll(".pyodide[data-install]").forEach((el) => {
      el.dataset.install = el.dataset.install
        .split(",")
        .map((pkg) => {
          const name = pkg.trim();
          if (!name.endsWith(".whl")) {
            return name;
          }
          return new URL(name.split("/").pop(), wheelsBase).href;
        })
        .join(",");
    });
  }

  function editors() {
    return [...document.querySelectorAll(".md-content .pyodide, article .pyodide")];
  }

  function waitIdle() {
    if (inflight === 0) {
      return Promise.resolve();
    }
    return new Promise((resolve) => idleWaiters.push(resolve));
  }

  function waitFor(predicate, timeoutMs) {
    return new Promise((resolve, reject) => {
      const started = Date.now();
      const tick = () => {
        if (predicate()) {
          resolve();
          return;
        }
        if (Date.now() - started > timeoutMs) {
          reject(new Error("timeout"));
          return;
        }
        requestAnimationFrame(tick);
      };
      tick();
    });
  }

  function cellFailed(output) {
    const text = (output && output.textContent) || "";
    return /Could not install|Traceback \(most recent call last\)/.test(text);
  }

  async function runOne(root) {
    const btn = root.querySelector("[id$='--run']");
    const output = root.querySelector("[id$='--output']");
    if (!btn) {
      return;
    }
    window.__ppdocsPyodideRoot = root;
    const startInflight = inflight;
    btn.click();
    await waitFor(
      () =>
        root.getAttribute("data-md-exec-state") === "loading" ||
        inflight > startInflight,
      30000,
    ).catch(() => {});
    await waitFor(
      () => root.getAttribute("data-md-exec-state") !== "loading",
      180000,
    );
    await new Promise((resolve) => setTimeout(resolve, 50));
    await waitIdle();
    if (cellFailed(output)) {
      throw new Error("cell failed");
    }
  }

  async function runAll(button) {
    const roots = editors();
    if (!roots.length) {
      return;
    }
    button.disabled = true;
    try {
      for (let i = 0; i < roots.length; i += 1) {
        button.textContent = `Running ${i + 1} / ${roots.length}…`;
        await runOne(roots[i]);
      }
      button.textContent = "Run all";
    } catch (err) {
      button.textContent = "Run all (stopped)";
      console.error(err);
      setTimeout(() => {
        button.textContent = "Run all";
      }, 2500);
    } finally {
      button.disabled = false;
    }
  }

  function insertRunAll() {
    document.querySelectorAll(".ppdocs-run-all").forEach((el) => el.remove());
    const roots = editors();
    if (roots.length < 2) {
      return;
    }

    const wrap = document.createElement("p");
    wrap.className = "ppdocs-run-all";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "md-button md-button--primary";
    btn.textContent = "Run all";
    btn.title =
      "Run every editor on this page, top to bottom. Reload first if you already ran cells.";
    btn.addEventListener("click", () => runAll(btn));
    wrap.appendChild(btn);

    const info = document.querySelector(
      ".md-content details.info, .md-content .admonition.info, article details.info, article .admonition.info",
    );
    if (info) {
      info.appendChild(wrap);
    } else {
      roots[0].before(wrap);
    }
  }

  rewriteInstallPaths();
  insertRunAll();
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(() => {
      rewriteInstallPaths();
      insertRunAll();
    });
  }

  async function injectShowPlot(pyodide) {
    const source = await (await fetch(helperUrl())).text();
    await pyodide.runPythonAsync(source);
    await pyodide.runPythonAsync(`
import builtins
builtins.show_plot = show_plot
builtins.prepare = prepare
builtins.load_tsv = load_tsv
`);

    const orig = pyodide.runPythonAsync.bind(pyodide);
    const bindHelpers = `
import builtins
g = globals()
for _name in ("show_plot", "load_tsv", "PhreeqPython", "np", "plt"):
    _val = getattr(builtins, _name, None)
    if _val is not None:
        g[_name] = _val
`;
    let preparing = false;
    pyodide.runPythonAsync = async function (code, options) {
      const isHelper = code === "prepare()" || code === bindHelpers;
      if (!isHelper) {
        inflight += 1;
      }
      try {
        if (!isHelper && !preparing) {
          preparing = true;
          try {
            await orig("prepare()");
            await orig(bindHelpers, options);
          } catch (err) {
            console.error("Failed to prepare example globals", err);
          } finally {
            preparing = false;
          }
        }
        return await orig(code, options);
      } finally {
        if (!isHelper) {
          inflight = Math.max(0, inflight - 1);
          if (inflight === 0) {
            idleWaiters.splice(0).forEach((resolve) => resolve());
          }
        }
      }
    };
  }

  function rememberEditor(event) {
    const root = event.target && event.target.closest && event.target.closest(".pyodide");
    if (root) {
      window.__ppdocsPyodideRoot = root;
    }
  }
  document.addEventListener("click", rememberEditor, true);
  document.addEventListener("keydown", rememberEditor, true);

  function wrapLoadPyodide() {
    const orig = window.loadPyodide;
    if (typeof orig !== "function" || orig._ppdocs) {
      return;
    }
    const wrapped = async function loadPyodideWithDocsHelpers(...args) {
      const pyodide = await orig.apply(this, args);
      try {
        await injectShowPlot(pyodide);
      } catch (err) {
        console.error("Failed to load docs plot helper", err);
      }
      return pyodide;
    };
    wrapped._ppdocs = true;
    window.loadPyodide = wrapped;
  }

  document.addEventListener(
    "load",
    (event) => {
      const el = event.target;
      if (!el || !el.src || el.tagName !== "SCRIPT" || !el.src.includes("pyodide")) {
        return;
      }
      wrapLoadPyodide();
    },
    true,
  );
})();
