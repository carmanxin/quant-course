// Global Pyodide singleton — loaded once, shared by all PythonPlayground instances
(function() {
  if (window.__pyodideReady) return;

  const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
  const PYODIDE_INDEX = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';

  window.__pyodideReady = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = PYODIDE_URL;
    script.onload = async () => {
      try {
        const pyodide = await loadPyodide({ indexURL: PYODIDE_INDEX });
        await pyodide.loadPackage(['numpy', 'micropip']);
        const micropip = pyodide.pyimport('micropip');
        const version = pyodide.runPython('import sys; sys.version.split()[0]');
        window.__pyodide = pyodide;
        window.__pyodideVersion = version;
        window.__micropip = micropip;
        console.log('Pyodide ready:', version);
        resolve(pyodide);
      } catch (e) {
        reject(e);
      }
    };
    script.onerror = () => reject(new Error('Pyodide CDN failed'));
    document.head.appendChild(script);
  });
})();
