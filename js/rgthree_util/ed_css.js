var styles = `
.ed-dialog-button-reset {
  position: relative;
  appearance: none;
  cursor: pointer;
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0;
  margin: 0;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-size: 0.7rem;
}

.rgthree-top-messages-container [type=waiting]::before {
  content: "⏱️";
}


.now-loading-dialog-container {
  position: fixed;
  z-index: 9999;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 5%; /* 부모 width의 10% 만큼 내려옴 */
}

.now-loading-dialog-container > div {
  position: relative;
  height: fit-content;
  padding: 4px;
  margin-top: -100px; /* re-set by JS */
  opacity: 0;
  transition: all 0.33s ease-in-out;
  z-index: 3;
}

.now-loading-dialog-container > div:last-child {
  z-index: 2;
}

.now-loading-dialog-container > div:not(.-show) {
  z-index: 1;
}

.now-loading-dialog-container > div.-show {
  opacity: 1;
  margin-top: 0px !important;
}

.now-loading-dialog-container > div.-show {
  opacity: 1;
  transform: translateY(0%);
}

.now-loading-dialog-container > div > div {
  position: relative;
  background: #fcfcfb;
  color: #52422b;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
  height: fit-content;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.88);
  padding: 18px 12px 6px 12px;  /* top right bottom left */
  border-radius: 4px;
  font-family: Arial, sans-serif;
  font-size: 14px;
  font-weight: bold;
  background-image: url(/extensions/efficiency-nodes-ED/assets/nowloading.gif);
  width: 300px;   /* GIF 가로 크기 */
  height: 300px;  /* GIF 세로 크기 */
  background-size: contain; /* 비율 유지해서 맞춤 */
}

.now-loading-dialog-container > div > div > span {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.now-loading-dialog-container > div > div > span svg {
  width: 20px;
  height: auto;
  margin-right: 8px;
}

.now-loading-dialog-container > div > div > span svg.icon-checkmark {
  fill: #2e9720;
}

.now-loading-dialog-container [type=warn]::before,
.now-loading-dialog-container [type=success]::before {
  content: "⚠️";
  display: inline-block;
  flex: 0 0 auto;
  font-size: 18px;
  margin-right: 4px;
  line-height: 1;
}

.now-loading-dialog-container [type=success]::before {
  content: "🎉";
}

.now-loading-dialog-container a {
  cursor: pointer;
  text-decoration: underline;
  color: #fc0;
  margin-left: 4px;
  display: inline-block;
  line-height: 1;
}

.now-loading-dialog-container a:hover {
  color: #fc0;
  text-decoration: none;
} 
`

const styleSheet = document.createElement("style");
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

const preloadImg_nowloading1 = new Image();
const preloadImg_nowloading2 = new Image();
preloadImg_nowloading1.src = "/extensions/efficiency-nodes-ED/assets/nowloading.gif";
preloadImg_nowloading2.src = "/extensions/efficiency-nodes-ED/assets/tap-waiting.gif";


