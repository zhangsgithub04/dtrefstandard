(function () {
  class StandardRef extends HTMLElement {
    async connectedCallback() {
      const baseUrl = "https://your-api.onrender.com";
      const symbol = this.getAttribute("symbol");
      const version = this.getAttribute("version");
      const latest = this.hasAttribute("latest");

      this.innerHTML = "<div>Loading...</div>";

      if (!symbol) {
        this.innerHTML = "<div>Missing symbol</div>";
        return;
      }

      try {
        let url;

        if (latest) {
          url = `${baseUrl}/standards/latest/${encodeURIComponent(symbol)}`;
        } else if (version) {
          url = `${baseUrl}/standards/by-symbol/${encodeURIComponent(symbol)}/${encodeURIComponent(version)}`;
        } else {
          this.innerHTML = "<div>Missing version or latest</div>";
          return;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(typeof data === "string" ? data : JSON.stringify(data));
        }

        this.render(data);
      } catch (err) {
        this.innerHTML = `<div>Error: ${err.message}</div>`;
      }
    }

    render(data) {
      this.innerHTML = `
        <div style="border:1px solid #ddd; border-radius:10px; padding:16px; margin:12px 0; font-family:Arial,sans-serif;">
          <div style="font-size:1.1rem; font-weight:700;">
            ${data.standardname} ${data.version || ""}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Symbol:</strong> ${data.symbol}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Organization:</strong> ${data.organization || ""}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Date:</strong> ${data.standard_date || ""}
          </div>
          <div style="margin-top:12px;">
            <strong>Description:</strong>
            <div>${data.description || ""}</div>
          </div>
          <div style="margin-top:12px;">
            <strong>Long Description:</strong>
            <div>${data.longdescription || ""}</div>
          </div>
          <div style="margin-top:12px;">
            <a href="${data.url}" target="_blank" rel="noopener noreferrer">Open standard</a>
          </div>
        </div>
      `;
    }
  }

  customElements.define("standard-ref", StandardRef);
})();
