import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "https://your-service.com")
API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    st.error("Missing MY_API_KEY environment variable")
    st.stop()

st.set_page_config(page_title="Standard UI", layout="wide")
st.title("Standards UI")

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


def api_headers():
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def handle_response(response):
    content_type = response.headers.get("content-type", "")

    if not response.ok:
        if "application/json" in content_type:
            try:
                data = response.json()
                raise Exception(data)
            except Exception:
                raise Exception(f"API error: {response.status_code}")
        else:
            raise Exception(f"API error: {response.status_code}")

    if "application/json" in content_type:
        return response.json()

    raise Exception("API did not return JSON")

def get_all_standards():
    r = requests.get(
        f"{API_BASE}/standards",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def get_count():
    r = requests.get(
        f"{API_BASE}/standards/count",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def get_by_id(standard_id):
    r = requests.get(
        f"{API_BASE}/standards/{standard_id}",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def get_by_symbol(symbol):
    r = requests.get(
        f"{API_BASE}/standards/by-symbol/{symbol}",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def get_latest_by_symbol(symbol):
    r = requests.get(
        f"{API_BASE}/standards/latest/{symbol}",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def get_by_symbol_version(symbol, version):
    r = requests.get(
        f"{API_BASE}/standards/by-symbol/{symbol}/{version}",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def create_standard(payload):
    r = requests.post(
        f"{API_BASE}/standards",
        json=payload,
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def update_standard(standard_id, payload):
    r = requests.patch(
        f"{API_BASE}/standards/{standard_id}",
        json=payload,
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def replace_standard(standard_id, payload):
    r = requests.put(
        f"{API_BASE}/standards/{standard_id}",
        json=payload,
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def delete_standard(standard_id):
    r = requests.delete(
        f"{API_BASE}/standards/{standard_id}",
        headers=api_headers(),
        timeout=30,
    )
    return handle_response(r)


def clean_optional(value):
    value = value.strip()
    return value if value else None


def to_float_or_none(value):
    value = value.strip()
    if not value:
        return None
    return float(value)

def clean_version(value):
    value = value.strip()
    return value if value else None

def build_full_payload(symbol, standardname, version, standard_date, description, longdescription, url, organization):
    return {
        "symbol": symbol.strip(),
        "standardname": standardname.strip(),
        "version": clean_version(version),
        "standard_date": clean_optional(standard_date),
        "description": clean_optional(description),
        "longdescription": clean_optional(longdescription),
        "url": clean_optional(url),
        "organization": clean_optional(organization),
    }


def build_patch_payload(symbol, standardname, version, standard_date, description, longdescription, url, organization):
    payload = {}

    if symbol.strip():
        payload["symbol"] = symbol.strip()
    if standardname.strip():
        payload["standardname"] = standardname.strip()

    version_clean = version.strip()
    if version_clean:
        payload["version"] = float(version_clean)

    if standard_date.strip():
        payload["standard_date"] = standard_date.strip()
    if description.strip():
        payload["description"] = description.strip()
    if longdescription.strip():
        payload["longdescription"] = longdescription.strip()
    if url.strip():
        payload["url"] = url.strip()
    if organization.strip():
        payload["organization"] = organization.strip()

    return payload


# Top info
col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption(f"API Base: {API_BASE}")
with col_b:
    if st.button("Reload"):
        st.rerun()

# Count
try:
    count_data = get_count()
    st.metric("Standard Count", count_data["count"])
except Exception as e:
    st.error(f"Could not load count: {e}")

tabs = st.tabs([
    "All Standards",
    "Lookup",
    "Create",
    "Update",
    "Replace",
    "Delete",
])

with tabs[0]:
    st.subheader("All Standards")
    try:
        standards = get_all_standards()
        if standards:
            st.dataframe(standards, use_container_width=True)
        else:
            st.info("No standards found.")
    except Exception as e:
        st.error(f"Could not load standards: {e}")

with tabs[1]:
    st.subheader("Lookup")

    lookup_mode = st.radio(
        "Lookup type",
        ["By ID", "By Symbol", "Latest By Symbol", "By Symbol + Version"],
        horizontal=True,
    )

    if lookup_mode == "By ID":
        standard_id = st.text_input("Standard ID", key="lookup_id")
        if st.button("Fetch by ID"):
            try:
                result = get_by_id(int(standard_id))
                st.json(result)
            except Exception as e:
                st.error(f"Lookup failed: {e}")

    elif lookup_mode == "By Symbol":
        symbol = st.text_input("Symbol", key="lookup_symbol")
        if st.button("Fetch by Symbol"):
            try:
                result = get_by_symbol(symbol.strip())
                st.json(result)
            except Exception as e:
                st.error(f"Lookup failed: {e}")

    elif lookup_mode == "Latest By Symbol":
        symbol = st.text_input("Symbol", key="lookup_latest_symbol")
        if st.button("Fetch Latest"):
            try:
                result = get_latest_by_symbol(symbol.strip())
                st.json(result)
            except Exception as e:
                st.error(f"Lookup failed: {e}")

    elif lookup_mode == "By Symbol + Version":
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Symbol", key="lookup_symbol_version_symbol")
        with col2:
            version = st.text_input("Version", key="lookup_symbol_version_version")

        if st.button("Fetch by Symbol + Version"):
            try:
                result = get_by_symbol_version(symbol.strip(), float(version))
                st.json(result)
            except Exception as e:
                st.error(f"Lookup failed: {e}")

with tabs[2]:
    st.subheader("Create Standard")

    with st.form("create_form"):
        symbol = st.text_input("Symbol")
        standardname = st.text_input("Standard Name")
        version = st.text_input("Version")
        standard_date = st.text_input("Standard Date (YYYY-MM-DD)")
        organization = st.text_input("Organization")
        url = st.text_input("URL")
        description = st.text_area("Description")
        longdescription = st.text_area("Long Description")

        submitted = st.form_submit_button("Create")

    if submitted:
        try:
            payload = build_full_payload(
                symbol,
                standardname,
                version,
                standard_date,
                description,
                longdescription,
                url,
                organization,
            )
            result = create_standard(payload)
            st.success("Standard created successfully.")
            st.json(result)
        except Exception as e:
            st.error(f"Create failed: {e}")

with tabs[3]:
    st.subheader("Update Standard (PATCH)")

    with st.form("update_form"):
        standard_id = st.text_input("Standard ID to Update")
        symbol = st.text_input("Symbol", key="u_symbol")
        standardname = st.text_input("Standard Name", key="u_name")
        version = st.text_input("Version", key="u_version")
        standard_date = st.text_input("Standard Date (YYYY-MM-DD)", key="u_date")
        organization = st.text_input("Organization", key="u_org")
        url = st.text_input("URL", key="u_url")
        description = st.text_area("Description", key="u_desc")
        longdescription = st.text_area("Long Description", key="u_longdesc")

        submitted = st.form_submit_button("Update")

    if submitted:
        try:
            payload = build_patch_payload(
                symbol,
                standardname,
                version,
                standard_date,
                description,
                longdescription,
                url,
                organization,
            )
            if not payload:
                st.error("No fields provided for update.")
            else:
                result = update_standard(int(standard_id), payload)
                st.success("Standard updated successfully.")
                st.json(result)
        except Exception as e:
            st.error(f"Update failed: {e}")

with tabs[4]:
    st.subheader("Replace Standard (PUT)")

    with st.form("replace_form"):
        standard_id = st.text_input("Standard ID to Replace")
        symbol = st.text_input("Symbol", key="r_symbol")
        standardname = st.text_input("Standard Name", key="r_name")
        version = st.text_input("Version", key="r_version")
        standard_date = st.text_input("Standard Date (YYYY-MM-DD)", key="r_date")
        organization = st.text_input("Organization", key="r_org")
        url = st.text_input("URL", key="r_url")
        description = st.text_area("Description", key="r_desc")
        longdescription = st.text_area("Long Description", key="r_longdesc")

        submitted = st.form_submit_button("Replace")

    if submitted:
        try:
            payload = build_full_payload(
                symbol,
                standardname,
                version,
                standard_date,
                description,
                longdescription,
                url,
                organization,
            )
            result = replace_standard(int(standard_id), payload)
            st.success("Standard replaced successfully.")
            st.json(result)
        except Exception as e:
            st.error(f"Replace failed: {e}")

with tabs[5]:
    st.subheader("Delete Standard")

    standard_id = st.text_input("Standard ID to Delete", key="delete_id")
    if st.button("Delete Standard"):
        try:
            result = delete_standard(int(standard_id))
            st.success("Standard deleted successfully.")
            st.json(result)
        except Exception as e:
            st.error(f"Delete failed: {e}")
