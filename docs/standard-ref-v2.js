(function () {
  class StandardRef extends HTMLElement {
    static get observedAttributes() {
      return ["symbol", "version", "latest", "base-url", "api-key", "show"];
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

    getShowFields() {
      const raw = this.getAttribute("show");

      if (!raw) {
        return [
          "standardname",
          "version",
          "symbol",
          "organization",
          "standard_date",
          "description",
          "longdescription",
          "url"
        ];
      }

      return raw
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);
    }

    hasField(name) {
      return this.getShowFields().includes(name);
    }

    escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    renderRow(label, value) {
      if (value === null || value === undefined || value === "") return "";
      return `
        <div style="margin-top:6px; color:#555;">
          <strong>${this.escapeHtml(label)}:</strong> ${this.escapeHtml(value)}
        </div>
      `;
    }

    renderBlock(label, value) {
      if (value === null || value === undefined || value === "") return "";
      return `
        <div style="margin-top:12px;">
          <strong>${this.escapeHtml(label)}:</strong>
          <div>${this.escapeHtml(value)}</div>
        </div>
      `;
    }

    render(data) {
      const title =
        this.hasField("standardname") || this.hasField("version")
          ? `
            <div style="font-size:1.1rem; font-weight:700;">
              ${this.hasField("standardname") ? this.escapeHtml(data.standardname || "") : ""}
              ${this.hasField("version") ? this.escapeHtml(data.version || "") : ""}
            </div>
          `
          : "";

      const symbolHtml = this.hasField("symbol")
        ? this.renderRow("Symbol", data.symbol)
        : "";

      const organizationHtml = this.hasField("organization")
        ? this.renderRow("Organization", data.organization)
        : "";

      const dateHtml = this.hasField("standard_date")
        ? this.renderRow("Date", data.standard_date)
        : "";

      const descriptionHtml = this.hasField("description")
        ? this.renderBlock("Description", data.description)
        : "";

      const longDescriptionHtml = this.hasField("longdescription")
        ? this.renderBlock("Long Description", data.longdescription)
        : "";

      const urlHtml =
        this.hasField("url") && data.url
          ? `<div style="margin-top:12px;">
               <a href="${this.escapeHtml(data.url)}" target="_blank" rel="noopener noreferrer">Open standard</a>
             </div>`
          : "";

      this.innerHTML = `
        <div style="border:1px solid #ddd; border-radius:10px; padding:16px; margin:12px 0; font-family:Arial,sans-serif;">
          ${title}
          ${symbolHtml}
          ${organizationHtml}
          ${dateHtml}
          ${descriptionHtml}
          ${longDescriptionHtml}
          ${urlHtml}
        </div>
      `;
    }
  }

  customElements.define("standard-ref", StandardRef);
})();
