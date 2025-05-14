// sliding_panel.js

// store open tabs & editor instances
const tabs    = {};
const editors = {};
let currentKey;

// panel elements (populated on DOMContentLoaded)
let panel, overlay, wrapper, tabBar, closeBtn;

// 1) Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {

  // grab your panel UI
  panel    = document.getElementById("pdf-panel");
  overlay  = document.getElementById("pdf-overlay");
  wrapper  = document.getElementById("editor-wrapper");
  tabBar   = document.getElementById("tab-bar");
  closeBtn = document.getElementById("close-panel");

  // sanity check
  if (![panel, overlay, wrapper, tabBar, closeBtn].every(el => el)) {
    console.error("[OnlyOffice] Missing panel elements");
    return;
  }

  // bind close
  closeBtn.addEventListener("click", hidePanel);
  overlay .addEventListener("click", hidePanel);

  // attach open-button handlers
  document.querySelectorAll(".open-panel").forEach(btn => {
    btn.addEventListener("click", () => {
      // build a doc object straight from data-attrs
      const doc = {
        key:         btn.dataset.key,
        referencedata: btn.dataset.referencedata,
        url:         btn.dataset.url,
        token:       btn.dataset.token,
        title:       btn.dataset.title,
        permissions: JSON.parse(btn.dataset.permissions),
        extension:   btn.dataset.extension,
      };
      openDocument(doc);
    });
  });


});

// 2) Show / hide panel
function showPanel() {
  panel.classList.remove("translate-x-full");
  overlay.classList.remove("opacity-0", "invisible");
}
function hidePanel() {
  panel.classList.add("translate-x-full");
  overlay.classList.add("opacity-0");
  setTimeout(() => overlay.classList.add("invisible"), 300);
  currentKey = null;
}


// 3) Tab highlighting
const activeClasses = ["border-b-2","border-blue-600","dark:border-blue-400"];
function highlightTab(key) {
  Object.entries(tabs).forEach(([k, btn]) => {
    activeClasses.forEach(cls => btn.classList.toggle(cls, k === key));
  });
}


// 4) Hide editors except current
function hideOtherEditors(key) {
  Array.from(wrapper.children).forEach(child => {
    child.style.display = (child.dataset.key === key) ? "block" : "none";
  });
}


// 5) Core openDocument logic
function openDocument(doc) {
  const { key, referencedata, title, url, token, permissions, extension } = doc;

  // -- TAB CREATE / SWITCH --
  if (!tabs[key]) {
    const tab = document.createElement("button");
    tab.textContent = title;
    tab.dataset.key = key;
    tab.className = "px-3 py-1 whitespace-nowrap dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800";
    tab.addEventListener("click", () => openDocument(doc));
    tabBar.appendChild(tab);
    tabs[key] = tab;
  }
  highlightTab(key);

  // -- PANEL & EDITOR SETUP --
  hideOtherEditors(key);
  if (editors[key]) {
    currentKey = key;
    showPanel();
    return;
  }

  // create container & iframe
  const container = document.createElement("div");
  container.dataset.key = key;
  container.id        = `editorWrapper_${key}`;
  Object.assign(container.style, {position:"absolute",top:0,right:0,bottom:0,left:0});
  wrapper.appendChild(container);

  const iframe = document.createElement("iframe");
  iframe.id        = `editor_${key}`;
  iframe.dataset.key = key;
  Object.assign(iframe.style, {width:"100%",height:"100%",border:0});
  container.appendChild(iframe);

  // build OnlyOffice config
  const config = {
    width:         "100%",
    height:        "100%",
    type:          "desktop",
    documentType:  extension,            // e.g. 'pdf','docx'
    token,
    tokenHeader:   "Authorization",
    tokenPrefix:   "Bearer ",
    referenceData: referencedata,
    document:      { key, url, title, permissions },
    editorConfig:  {
      mode:         mode,
      callbackUrl:  callbackUrl,
      user: { 
        id: user_id, 
        name: user_name,
        info: "",
      } ,
      customization:{
        uiTheme:   "theme-light",
        autosave:  true,
        forcesave: true,
      }
    }
  };

  // initialize
  try {
    const instance = new DocsAPI.DocEditor(iframe.id, config);
    editors[key]    = { instance, container };
    currentKey      = key;
    showPanel();
  } catch(err) {
    console.error("[OnlyOffice] init failed for", key, err);
  }
}

// sliding_panel.js

// 1) Grab the button & track state
const generateBtn     = document.getElementById("generate-pdf-btn");
let   hasGeneratedOne = false;

generateBtn.addEventListener("click", async () => {
  // 2) On second+ click, confirm
  if (hasGeneratedOne) {
    const ok = confirm("Are you sure you want to add another file?");
    if (!ok) return;
  }
  hasGeneratedOne = true;

  // 3) Show “Please wait…” and disable
  const waitMsg = document.createElement("div");
  waitMsg.id        = "pdf-wait-msg";
  waitMsg.className = "text-sm text-gray-700 dark:text-gray-300 mb-2";
  waitMsg.textContent = "Processing";
  generateBtn.insertAdjacentElement("afterend", waitMsg);
  generateBtn.disabled = true;

  try {
    // 4) Fetch the new PDF
    const resp = await fetch(
      `/oneglance/generate_pdf/?directory_path=data&file_extension=pdf`
    );
    const doc = await resp.json();
    if (doc.error) {
      console.error("Generation failed:", doc.error);
      return;
    }

    // 5) Build payload for openDocument()
    const payload = {
      key:         doc.key,
      url:         doc.url,
      token:       doc.token,
      title:       doc.title,             // must match your JSON
      extension:   doc.extension || "pdf",
      permissions: doc.permissions || doc.perms
    };

    // 6) Create new <li><button>
    const li  = document.createElement("li");
    const btn = document.createElement("button");
    btn.type      = "button";
    btn.className = "open-panel flex items-center text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-500 focus:outline-none";
    btn.innerHTML = `
      <i class="fa-solid fa-file-circle-plus mr-2" aria-hidden="true"></i><span class="font-medium">${payload.title}</span>
    `;
    // 7) Set data-attrs your panel code reads
    btn.dataset.key         = payload.key;
    btn.dataset.url         = payload.url;
    btn.dataset.token       = payload.token;
    btn.dataset.title       = payload.title;
    btn.dataset.extension   = payload.extension;
    btn.dataset.permissions = JSON.stringify(payload.permissions);

    li.appendChild(btn);
    // 8) Append into your UL#document-list
    document.getElementById("document-list").appendChild(li);

    // 9) Wire it up and open immediately
    btn.addEventListener("click", () => openDocument(payload));
    btn.click();

  } catch (err) {
    console.error("Unexpected error:", err);
  } finally {
    // 10) Clean up “Please wait…” & re-enable button
    document.getElementById("pdf-wait-msg")?.remove();
    generateBtn.disabled = false;
  }
});
