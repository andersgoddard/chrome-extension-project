function extractPostcodeAndEpc(html) {
  console.log("[extractPostcodeAndEpc] Starting extraction...");
  const marker = "window.adInfo =";
  const startIndex = html.indexOf(marker);
  if (startIndex === -1) {
    console.warn("[extractPostcodeAndEpc] Marker not found.");
    return null;
  }

  const jsonStart = html.indexOf("{", startIndex);
  if (jsonStart === -1) {
    console.warn("[extractPostcodeAndEpc] JSON start not found.");
    return null;
  }

  let braceDepth = 0;
  let jsonEnd = -1;

  for (let i = jsonStart; i < html.length; i++) {
    if (html[i] === "{") braceDepth++;
    else if (html[i] === "}") {
      braceDepth--;
      if (braceDepth === 0) {
        jsonEnd = i + 1;
        break;
      }
    }
  }

  if (jsonEnd === -1) {
    console.warn("[extractPostcodeAndEpc] JSON end not found.");
    return null;
  }

  const jsonStr = html.substring(jsonStart, jsonEnd);
  console.log("[extractPostcodeAndEpc] Extracted JSON string length:", jsonStr.length);

  try {
    const data = JSON.parse(jsonStr);
    console.log("[extractPostcodeAndEpc] Parsed JSON:", data);

    const propertyData = data.propertyData || {};
    const address = propertyData.address || {};
    const outcode = address.outcode || "";
    const incode = address.incode || "";
    const postcode = outcode && incode ? `${outcode} ${incode}` : null;

    const epcGraphs = propertyData.epcGraphs || [];
    const epcUrl = epcGraphs.length > 0 ? epcGraphs[0].url : null;

    // Log immediately after extraction
    console.log(`[extractPostcodeAndEpc] Extracted postcode: "${postcode}", EPC URL: "${epcUrl}"`);

    if (!postcode) {
      console.warn("[extractPostcodeAndEpc] Postcode not found in data.");
      return null;
    }

    return {
      postcode,
      epc_url: epcUrl
    };
  } catch (e) {
    console.error("[extractPostcodeAndEpc] Failed to parse JSON:", e);
    return null;
  }
}

(async () => {
  console.log("[content.js] Running extraction and POST script.");
  try {
    const html = document.documentElement.innerHTML;
    const result = extractPostcodeAndEpc(html);

    if (!result) {
      console.warn("[content.js] Extraction returned null, aborting.");
      return;
    }

    // Log postcode and EPC URL right here as well, just in case
    console.log(`[content.js] Post-extraction data - postcode: "${result.postcode}", EPC URL: "${result.epc_url}"`);

    const payload = {
      url: window.location.href,
      postcode: result.postcode,
      epc_url: result.epc_url || null
    };

    console.log("[content.js] Payload to send:", payload);

    const response = await fetch("https://rightmove-activity-monitor.onrender.com/add-rightmove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    console.log("[content.js] Fetch response status:", response.status);

    if (!response.ok) {
      console.error("[content.js] POST failed:", response.statusText);
      return;
    }

    const responseData = await response.json();
    console.log("[content.js] POST response JSON:", responseData);

  } catch (err) {
    console.error("[content.js] Unexpected error:", err);
  }
})();
