const EXTENSION_ID = "lentera-digital-judol-detector";
const inference_url = "http://127.0.0.1:5000/inference"

function generatePopupContentWarning(classificationResult) {
  document.querySelector(`#${EXTENSION_ID}-popup-overlay`)?.remove();

  const overlay = document.createElement('div');
  overlay.id = `${EXTENSION_ID}-popup-overlay`;
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100vw';
  overlay.style.height = '100vh';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  overlay.style.zIndex = '999';
  overlay.style.display = 'flex';
  overlay.style.justifyContent = 'center';
  overlay.style.alignItems = 'center';

  const popup = document.createElement('div');
  popup.id = `${EXTENSION_ID}-popup`;
  popup.style.backgroundColor = 'white';
  popup.style.border = '1px solid black';
  popup.style.color = 'black';
  popup.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.3)';
  popup.style.borderRadius = '6px';
  popup.style.zIndex = '1000';

  if (!classificationResult) return;
  if (classificationResult && classificationResult === 'aman') return;

  popup.innerHTML = `
    <div
      id="${EXTENSION_ID}-popup-content"
      style="
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #ffffff;
        color: #1f1f1f;
        padding: 24px 20px;
        width: 360px;
        max-width: 90vw;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        text-align: center;
      "
    >
      <div
        style="
          font-size: 20px;
          font-weight: bold;
          color: #d32f2f;
          margin-bottom: 12px;
        "
      >
        ⚠️ Perhatian!
      </div>

      <p
        style="
          font-size: 15px;
          line-height: 1.5;
          margin: 0 0 40px 0;
        "
      >
        Sistem kami mendeteksi bahwa Anda sedang mengakses situs yang tergolong <strong>judi online</strong>. Aktivitas ini akan dilaporkan. Silakan tinggalkan situs ini segera untuk menghindari konsekuensi lebih lanjut.
      </p>

      <button
        id="${EXTENSION_ID}-close-popup"
        style="
          background-color: #d32f2f;
          color: white;
          border: none;
          padding: 10px 30px;
          font-size: 14px;
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 0.3s ease;
        "
        onmouseover="this.style.backgroundColor='#b71c1c'"
        onmouseout="this.style.backgroundColor='#d32f2f'"
      >
        Tutup
      </button>
    </div>
  `;

  popup.querySelector(`#${EXTENSION_ID}-close-popup`).addEventListener('click', () => {
    overlay.remove();
  });

  overlay.appendChild(popup);
  document.body.appendChild(overlay);
}

async function main() {

  try {
    const url = new URL(window.location.href);
    const domain = url.hostname;

    const classificationResult = await fetch(inference_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        url: domain,
      })
    });

    // if (!classificationResult.ok) {
    //   throw new Error(`HTTP error! status: ${classificationResult.status}`);
    // }

    // const result = await classificationResult.json();
    // console.log("Classification Result:", result);

    // if (result) {
    //   generatePopupContentWarning(result.label);
    // } else {
    //   console.warn("No classification result available.");
    // }
  } catch (error) {
    console.error("Error during inference:", error);
  }
}

main();