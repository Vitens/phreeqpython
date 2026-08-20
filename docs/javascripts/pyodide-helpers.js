(function () {
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

  rewriteInstallPaths();
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(rewriteInstallPaths);
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
    let preparing = false;
    pyodide.runPythonAsync = async function (code, options) {
      if (!preparing) {
        preparing = true;
        try {
          await orig("prepare()", options);
        } catch (err) {
          console.error("Failed to prepare example globals", err);
        } finally {
          preparing = false;
        }
      }
      return orig(code, options);
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
