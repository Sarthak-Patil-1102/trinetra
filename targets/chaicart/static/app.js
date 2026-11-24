// ChaiCart frontend (demo).
// VULN: an API key shipped straight into the browser bundle — anyone can read it.
const API_KEY = "sk_live_frontend_leaked_key_987654";

async function loadProducts() {
  const r = await fetch("/products", { headers: { "x-api-key": API_KEY } });
  return r.json();
}
