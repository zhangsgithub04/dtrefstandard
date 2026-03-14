(function () {
  class StandardRef extends HTMLElement {
    static get observedAttributes() {
      return ["symbol", "version", "latest", "base-url", "api-key", "show", "display"];
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

      this.innerHTML = "Loading...";

      if (!symbol) {
        this.innerHTML = "Missing symbol";
        return;
      }

      try {
        let url;

        if (latest) {
          url = `${baseUrl}/standards/latest/${encodeURIComponent(symbol)}`;
        } else if (version) {
          url = `${baseUrl}/standards/by-symbol/${encodeURIComponent(symbol)}/${encodeURIComponent(version)}`;
        } else {
          this.innerHTML = "Missing version or latest";
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
        this.innerHTML = `Error: ${this.escapeHtml(err.message)}`;
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

    isInline() {
      return this.getAttribute("display") === "inline";
    }

    escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    formatInlineText(data) {
      const parts = [];

      if (this.hasField("standardname") && data.standardname) {
        parts.push(this.escapeHtml(data.standardname));
      }

      if (this.hasField("version") && data.version) {
        parts.push(this.escapeHtml(data.version));
      }

      if (this.hasField("symbol") && data.symbol) {
        parts.push(this.escapeHtml(data.symbol));
      }

      if (this.hasField("organization") && data.organization) {
        parts.push(this.escapeHtml(data.organization));
      }

      if (this.hasField("standard_date") && data.standard_date) {
        parts.push(this.escapeHtml(data.standard_date));
      }

      if (this.hasField("description") && data.description) {
        parts.push(this.escapeHtml(data.description));
      }

      if (this.hasField("longdescription") && data.longdescription) {
        parts.push(this.escapeHtml(data.longdescription));
      }

      if (this.hasField("url") && data.url) {
        parts.push(
          `<a href="${this.escapeHtml(data.url)}" target="_blank" rel="noopener noreferrer">${this.escapeHtml(data.url)}</a>`
        );
      }

      return parts.join(" ");
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
      if (this.isInline()) {
        this.innerHTML = this.formatInlineText(data);
        this.style.display = "inline";
        return;
      }

      this.style.display = "block";

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
