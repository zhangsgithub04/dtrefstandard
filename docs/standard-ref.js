(function () {
  class StandardRef extends HTMLElement {
    static get observedAttributes() {
      return ["symbol", "version", "latest", "base-url", "api-key"];
    }

    connectedCallback() {
      this.load();
    }

    attributeChangedCallback() {
      if (this.isConnected) {
        this.load();
      }
    }

    async load() {
      const baseUrl =
        this.getAttribute("base-url") || "https://dtrefstandard.onrender.com";
      const apiKey = this.getAttribute("api-key") || "oneontacs";
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

        const headers = {
          "Content-Type": "application/json"
        };

        if (apiKey) {
          headers["X-API-Key"] = apiKey;
        }

        const response = await fetch(url, {
          method: "GET",
          headers
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
          ? await response.json()
          : await response.text();

        if (!response.ok) {
          throw new Error(typeof data === "string" ? data : JSON.stringify(data));
        }

        this.render(data);
      } catch (err) {
        this.innerHTML = `<div>Error: ${this.escapeHtml(err.message)}</div>`;
      }
    }

    escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    render(data) {
      const urlHtml = data.url
        ? `<div style="margin-top:12px;">
             <a href="${this.escapeHtml(data.url)}" target="_blank" rel="noopener noreferrer">Open standard</a>
           </div>`
        : "";

      const descriptionHtml = data.description
        ? `<div style="margin-top:12px;">
             <strong>Description:</strong>
             <div>${this.escapeHtml(data.description)}</div>
           </div>`
        : "";

      const longDescriptionHtml = data.longdescription
        ? `<div style="margin-top:12px;">
             <strong>Long Description:</strong>
             <div>${this.escapeHtml(data.longdescription)}</div>
           </div>`
        : "";

      this.innerHTML = `
        <div style="border:1px solid #ddd; border-radius:10px; padding:16px; margin:12px 0; font-family:Arial,sans-serif;">
          <div style="font-size:1.1rem; font-weight:700;">
            ${this.escapeHtml(data.standardname || "")} ${this.escapeHtml(data.version || "")}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Symbol:</strong> ${this.escapeHtml(data.symbol || "")}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Organization:</strong> ${this.escapeHtml(data.organization || "")}
          </div>
          <div style="margin-top:6px; color:#555;">
            <strong>Date:</strong> ${this.escapeHtml(data.standard_date || "")}
          </div>
          ${descriptionHtml}
          ${longDescriptionHtml}
          ${urlHtml}
        </div>
      `;
    }
  }

  customElements.define("standard-ref", StandardRef);
})();
