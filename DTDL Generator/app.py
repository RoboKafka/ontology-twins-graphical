import streamlit as st
import json

# ---------- Helper Functions ----------
def generate_dtdl(model_id, display_name, elements, version=1):
    model = {
        "@id": f"dtmi:ex:domain:{model_id};{version}",
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": display_name,
        "contents": elements
    }
    return model

def dtdl_type_to_postgres(dtype):
    mapping = {
        "string": "TEXT",
        "double": "DOUBLE PRECISION",
        "integer": "INTEGER",
        "boolean": "BOOLEAN"
    }
    return mapping.get(dtype, "TEXT")

def generate_postgres_schema(model_id, elements):
    cols = ["id SERIAL PRIMARY KEY"]
    for e in elements:
        if e["@type"] in ["Property", "Telemetry"]:
            if isinstance(e["schema"], str):
                pg_type = dtdl_type_to_postgres(e["schema"])
                cols.append(f"{e['name']} {pg_type}")
            elif isinstance(e["schema"], dict) and e["schema"].get("@type") == "Enum":
                cols.append(f"{e['name']} TEXT")
    table_name = model_id.lower()
    schema = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(cols) + "\n);"
    return schema


# ---------- Streamlit UI ----------
st.title("DTDL Model and Postgres Schema Generator")

st.sidebar.header("Model Info")
model_id = st.sidebar.text_input("Model ID (e.g. ProjectCell)", "ProjectCell")
display_name = st.sidebar.text_input("Display Name", "Project Cell")
version = st.sidebar.number_input("Version", min_value=1, value=1)

if "elements" not in st.session_state:
    st.session_state["elements"] = []

# Layout: two columns
col1, col2 = st.columns([2, 1])

with col1:
    # ---------- Section: Add Property ----------
    st.header("Add Property")
    with st.form("property_form", clear_on_submit=True):
        name = st.text_input("Property Name")
        dtype = st.selectbox("Data Type", ["string", "double", "integer", "boolean", "enum"])
        enum_values = []
        if dtype == "enum":
            enum_input = st.text_area("Enum Values (comma-separated)", "ON, OFF, Maintenance")
            enum_values = [v.strip() for v in enum_input.split(",") if v.strip()]
        submitted = st.form_submit_button("Add Property")
        if submitted and name:
            if dtype == "enum":
                st.session_state["elements"].append({
                    "@type": "Property",
                    "name": name,
                    "schema": {
                        "@type": "Enum",
                        "valueSchema": "string",
                        "enumValues": [{"name": v, "enumValue": v} for v in enum_values]
                    }
                })
            else:
                st.session_state["elements"].append({
                    "@type": "Property",
                    "name": name,
                    "schema": dtype
                })

    # ---------- Section: Add Telemetry ----------
    st.header("Add Telemetry")
    with st.form("telemetry_form", clear_on_submit=True):
        tname = st.text_input("Telemetry Name")
        tdtype = st.selectbox("Telemetry Data Type", ["string", "double", "integer", "boolean", "enum"])
        tenum_values = []
        if tdtype == "enum":
            enum_input = st.text_area("Enum Values (comma-separated)", "Idle, Running, Fault")
            tenum_values = [v.strip() for v in enum_input.split(",") if v.strip()]
        tsubmitted = st.form_submit_button("Add Telemetry")
        if tsubmitted and tname:
            if tdtype == "enum":
                st.session_state["elements"].append({
                    "@type": "Telemetry",
                    "name": tname,
                    "schema": {
                        "@type": "Enum",
                        "valueSchema": "string",
                        "enumValues": [{"name": v, "enumValue": v} for v in tenum_values]
                    }
                })
            else:
                st.session_state["elements"].append({
                    "@type": "Telemetry",
                    "name": tname,
                    "schema": tdtype
                })

    # ---------- Section: Add Command ----------
    st.header("Add Command")
    with st.form("command_form", clear_on_submit=True):
        cname = st.text_input("Command Name")
        crequest = st.text_area("Request Schema (optional JSON)")
        cresponse = st.text_area("Response Schema (optional JSON)")
        csubmitted = st.form_submit_button("Add Command")
        if csubmitted and cname:
            cmd = {"@type": "Command", "name": cname}
            if crequest:
                try:
                    cmd["request"] = json.loads(crequest)
                except:
                    st.error("Invalid JSON for request schema")
            if cresponse:
                try:
                    cmd["response"] = json.loads(cresponse)
                except:
                    st.error("Invalid JSON for response schema")
            st.session_state["elements"].append(cmd)

    # ---------- Section: Add Relationship ----------
    st.header("Add Relationship")
    with st.form("relationship_form", clear_on_submit=True):
        rname = st.text_input("Relationship Name")
        rtarget = st.text_input("Target Model (e.g. dtmi:ex:domain:RobotArm;1)")
        rmin = st.number_input("Min Multiplicity", min_value=0, value=0)
        rmax = st.number_input("Max Multiplicity (0 = unlimited)", min_value=0, value=1)
        rsubmitted = st.form_submit_button("Add Relationship")
        if rsubmitted and rname and rtarget:
            rel = {
                "@type": "Relationship",
                "name": rname,
                "target": rtarget,
                "minMultiplicity": rmin
            }
            if rmax > 0:
                rel["maxMultiplicity"] = rmax
            st.session_state["elements"].append(rel)

with col2:
    st.subheader("Current Model Contents")
    for e in st.session_state["elements"]:
        st.json(e)

# ---------- Generate Model and Schema ----------
if st.button("Generate Outputs"):
    model = generate_dtdl(model_id, display_name, st.session_state["elements"], version)
    dtdl_json = json.dumps(model, indent=2)
    pg_schema = generate_postgres_schema(model_id, st.session_state["elements"])

    st.subheader("Generated DTDL")
    st.code(dtdl_json, language="json")

    st.download_button(
        label="Download DTDL JSON",
        data=dtdl_json,
        file_name=f"{model_id}.json",
        mime="application/json"
    )

    st.subheader("Generated Postgres Schema")
    st.code(pg_schema, language="sql")

    st.download_button(
        label="Download SQL Schema",
        data=pg_schema,
        file_name=f"{model_id}.sql",
        mime="text/sql"
    )
