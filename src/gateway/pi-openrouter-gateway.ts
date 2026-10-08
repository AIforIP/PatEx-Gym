import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  const configured = process.env.PI_GATEWAY_BASE_URL || "http://127.0.0.1:7000";
  const root = configured.replace(/\/v1\/?$/, "").replace(/\/$/, "");
  pi.registerProvider("openrouter", {
    baseUrl: `${root}/v1`,
  });
}
