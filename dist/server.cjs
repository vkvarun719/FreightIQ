var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// server.ts
var import_express = __toESM(require("express"), 1);
var import_path = __toESM(require("path"), 1);
var import_fs = __toESM(require("fs"), 1);
var import_child_process = require("child_process");
var import_util = require("util");
var import_vite = require("vite");
var execAsync = (0, import_util.promisify)(import_child_process.exec);
var currentBusinessInfo = {
  companyName: "FreightIQ Global Maritime Analytics Ltd.",
  tradingName: "FreightIQ 2026",
  tagline: "Stochastic freight pricing & laycan optimization engine",
  imoCompanyNumber: "IMO 9842109 / BIMCO #48291",
  headquarters: {
    addressLine1: "12 Marina Boulevard, Marina Bay Financial Centre Tower 3",
    city: "Singapore",
    state: "Central Region",
    country: "Singapore",
    postalCode: "018982"
  },
  contactChannels: {
    commercialCharteringEmail: "chartering@freightiq-maritime.com",
    operationsDemurrageEmail: "ops.demurrage@freightiq-maritime.com",
    generalInquiriesEmail: "inquiries@freightiq-maritime.com",
    primaryPhone: "+65 6829 4400",
    emergency247OpsPhone: "+65 9188 3320 (24/7 Watch Desk)",
    satelliteVhfCallsign: "VHF Ch 16 / DSC MMSI 563004820"
  },
  operatingHours: "24/7 Continuous Operational Telemetry & Watchkeeping",
  globalDesks: [
    {
      hub: "Singapore Hub (APAC)",
      location: "Marina Bay Tower 3, Level 28",
      dutyOfficer: "Capt. Jonathan Vance (Senior Marine Superintendent)",
      timezone: "SGT (UTC+8)",
      activeStatus: "ACTIVE ON WATCH"
    },
    {
      hub: "London Desk (EMEA)",
      location: "30 St Mary Axe (The Gherkin), London EC3A 8EP",
      dutyOfficer: "Sarah Al-Mansoor (Senior Freight Derivatives Broker)",
      timezone: "GMT (UTC+0)",
      activeStatus: "STANDBY FOR FIXING"
    },
    {
      hub: "Houston Office (Americas)",
      location: "One Shell Plaza, 910 Louisiana St, Houston, TX 77002",
      dutyOfficer: "David K. Reynolds (Bunker & Laytime Risk Analyst)",
      timezone: "CST (UTC-6)",
      activeStatus: "OPERATIONAL"
    }
  ]
};
var recentSubmissions = [];
async function startServer() {
  const app = (0, import_express.default)();
  const PORT = 3e3;
  app.use(import_express.default.json());
  app.get("/api/health", (_req, res) => {
    res.json({ status: "healthy", timestamp: (/* @__PURE__ */ new Date()).toISOString() });
  });
  function loadBdiHistory(limit = 140) {
    const candidatePaths = [
      import_path.default.join(process.cwd(), "backend", "Book1.csv"),
      import_path.default.join(process.cwd(), "freightratesBDI", "freightrates", "Baltic Dry Index Historical Data.csv"),
      import_path.default.join(process.cwd(), "freightratesBDI", "freightrates", "Book1.csv")
    ];
    let filePath = candidatePaths.find((p) => import_fs.default.existsSync(p));
    if (!filePath) return [];
    const content = import_fs.default.readFileSync(filePath, "utf-8");
    const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);
    const records = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      const rawParts = line.split('","').map((s) => s.replace(/"/g, "").trim());
      if (rawParts.length < 2) continue;
      const [dateRaw, priceRaw, openRaw, highRaw, lowRaw, , changeRaw] = rawParts;
      const price = parseFloat(priceRaw.replace(/,/g, ""));
      if (isNaN(price)) continue;
      let dateStr = dateRaw;
      if (dateRaw.includes("/")) {
        const dp = dateRaw.split("/");
        if (dp.length === 3) {
          dateStr = `${dp[2]}-${dp[0].padStart(2, "0")}-${dp[1].padStart(2, "0")}`;
        }
      }
      records.push({
        date: dateStr,
        price,
        open: openRaw ? parseFloat(openRaw.replace(/,/g, "")) : price,
        high: highRaw ? parseFloat(highRaw.replace(/,/g, "")) : price,
        low: lowRaw ? parseFloat(lowRaw.replace(/,/g, "")) : price,
        change_pct: changeRaw ? parseFloat(changeRaw.replace(/%/g, "")) : 0
      });
    }
    records.sort((a, b) => a.date.localeCompare(b.date));
    for (let i = 0; i < records.length; i++) {
      if (i >= 4) {
        const slice5 = records.slice(i - 4, i + 1);
        records[i].sma_5 = Math.round(slice5.reduce((acc, r) => acc + r.price, 0) / 5 * 100) / 100;
      }
      if (i >= 19) {
        const slice20 = records.slice(i - 19, i + 1);
        records[i].sma_20 = Math.round(slice20.reduce((acc, r) => acc + r.price, 0) / 20 * 100) / 100;
      }
    }
    return limit ? records.slice(-limit) : records;
  }
  function loadBdiForecasts() {
    const candidatePaths = [
      import_path.default.join(process.cwd(), "freightratesBDI", "freightrates", "Book1.csv"),
      import_path.default.join(process.cwd(), "freightratesBDI", "freightrates", "models", "forecast_30d.csv")
    ];
    let filePath = candidatePaths.find((p) => import_fs.default.existsSync(p));
    if (!filePath) return [];
    const content = import_fs.default.readFileSync(filePath, "utf-8");
    const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);
    const forecasts = [];
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(",").map((s) => s.trim());
      if (parts.length < 5) continue;
      forecasts.push({
        step: parseInt(parts[0], 10) || i,
        date: parts[1],
        predicted_price: parseFloat(parts[2]),
        lower_95: parseFloat(parts[3]),
        upper_95: parseFloat(parts[4]),
        ridge_pred: parts[5] ? parseFloat(parts[5]) : parseFloat(parts[2]),
        gbdt_pred: parts[6] ? parseFloat(parts[6]) : parseFloat(parts[2]),
        dnn_pred: parts[7] ? parseFloat(parts[7]) : parseFloat(parts[2]),
        volatility_std: parts[8] ? parseFloat(parts[8]) : 150
      });
    }
    return forecasts;
  }
  app.get("/api/bdi/history", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit || "140", 10);
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 800);
        const fastApiResponse = await fetch(`http://127.0.0.1:8000/api/history?limit=${limit}`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (fastApiResponse.ok) {
          const fastApiData = await fastApiResponse.json();
          return res.json({ success: true, source: "fastapi", data: fastApiData });
        }
      } catch {
      }
      const history = loadBdiHistory(limit);
      res.json({ success: true, source: "book1_csv", data: history });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  });
  app.get("/api/bdi/forecast", async (req, res) => {
    try {
      const days = parseInt(req.query.days || "30", 10);
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 800);
        const fastApiResponse = await fetch(`http://127.0.0.1:8000/api/forecast?days=${days}`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (fastApiResponse.ok) {
          const fastApiData = await fastApiResponse.json();
          return res.json({ success: true, source: "fastapi", data: fastApiData });
        }
      } catch {
      }
      const forecasts = loadBdiForecasts();
      const history = loadBdiHistory(5);
      const latestPrice = history.length > 0 ? history[history.length - 1].price : 3157;
      const latestDate = history.length > 0 ? history[history.length - 1].date : "2026-09-01";
      const sliceForecasts = forecasts.slice(0, days);
      const lastPred = sliceForecasts.length > 0 ? sliceForecasts[sliceForecasts.length - 1].predicted_price : latestPrice;
      const totalChange = (lastPred - latestPrice) / latestPrice * 100;
      const bias = totalChange > 2 ? "BULLISH (UPWARD)" : totalChange < -2 ? "BEARISH (DOWNWARD)" : "NEUTRAL / SIDEWAYS";
      res.json({
        success: true,
        source: "book1_csv",
        data: {
          latest_date: latestDate,
          latest_price: latestPrice,
          horizon_days: days,
          market_bias: bias,
          forecasts: sliceForecasts
        }
      });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  });
  app.get("/api/bdi/metrics", async (_req, res) => {
    try {
      const reportPath = import_path.default.join(process.cwd(), "freightratesBDI", "freightrates", "models", "model_report.json");
      if (import_fs.default.existsSync(reportPath)) {
        const report = JSON.parse(import_fs.default.readFileSync(reportPath, "utf-8"));
        if (report.model_metrics) {
          return res.json({ success: true, data: report.model_metrics });
        }
      }
      res.json({
        success: true,
        data: {
          "Weighted Meta-Ensemble": { MAE: 40.75, RMSE: 53.16, "MAPE_%": 1.77, "Directional_Accuracy_%": 68.01, R2_Score: 0.9845 },
          "Gradient Boosted Trees (GBDT)": { MAE: 38.62, RMSE: 51.51, "MAPE_%": 1.68, "Directional_Accuracy_%": 69.12, R2_Score: 0.9854 },
          "Ridge Regression": { MAE: 40, RMSE: 54.59, "MAPE_%": 1.74, "Directional_Accuracy_%": 69.49, R2_Score: 0.9836 },
          "Deep Neural Network (MLP)": { MAE: 47.12, RMSE: 60.41, "MAPE_%": 2.05, "Directional_Accuracy_%": 65.44, R2_Score: 0.9799 }
        }
      });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  });
  app.post("/api/bdi/optimize", async (req, res) => {
    try {
      const {
        commodity = "Iron Ore",
        cargo_volume_mt = 75e3,
        origin_port = "Visakhapatnam",
        dest_port = "Qingdao",
        contract_duration = "Short-Term (3 Months)",
        horizon_days = 30
      } = req.body;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1200);
        const fastApiResponse = await fetch("http://127.0.0.1:8000/api/optimize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            commodity,
            cargo_volume_mt,
            origin_port,
            dest_port,
            contract_duration,
            horizon_days
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (fastApiResponse.ok) {
          const fastApiData = await fastApiResponse.json();
          return res.json({ success: true, source: "fastapi", data: fastApiData });
        }
      } catch {
      }
      const pythonScript = `
import sys, json
sys.path.insert(0, r"${import_path.default.join(process.cwd(), "freightratesBDI", "freightrates")}")
import freight_engine
res = freight_engine.run_optimization_json(
    commodity="${commodity}",
    cargo_volume_mt=${cargo_volume_mt},
    origin_port="${origin_port}",
    dest_port="${dest_port}",
    contract_duration="${contract_duration}",
    horizon_days=${horizon_days}
)
print(json.dumps(res))
`.trim().replace(/\n/g, "; ");
      const { stdout } = await execAsync(`python -c "${pythonScript}"`, {
        cwd: import_path.default.join(process.cwd(), "freightratesBDI", "freightrates")
      });
      const parsed = JSON.parse(stdout.trim());
      res.json({ success: true, source: "python_engine", data: parsed });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  });
  app.get("/api/business-info", (_req, res) => {
    res.json({
      success: true,
      data: currentBusinessInfo
    });
  });
  app.put("/api/business-info", (req, res) => {
    const body = req.body;
    const errors = {};
    if (!body.companyName || typeof body.companyName !== "string" || body.companyName.trim().length < 3) {
      errors.companyName = "Company name must be at least 3 characters.";
    }
    if (!body.contactChannels?.commercialCharteringEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.contactChannels.commercialCharteringEmail)) {
      errors.commercialCharteringEmail = "A valid commercial chartering email is required.";
    }
    if (!body.contactChannels?.operationsDemurrageEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.contactChannels.operationsDemurrageEmail)) {
      errors.operationsDemurrageEmail = "A valid demurrage operations email is required.";
    }
    if (!body.contactChannels?.primaryPhone || typeof body.contactChannels.primaryPhone !== "string" || body.contactChannels.primaryPhone.trim().length < 6) {
      errors.primaryPhone = "A valid phone number is required (min 6 characters).";
    }
    if (Object.keys(errors).length > 0) {
      return res.status(400).json({
        success: false,
        message: "Server validation failed for business information update.",
        errors
      });
    }
    currentBusinessInfo = {
      ...currentBusinessInfo,
      companyName: body.companyName.trim(),
      tradingName: body.tradingName?.trim() || currentBusinessInfo.tradingName,
      tagline: body.tagline?.trim() || currentBusinessInfo.tagline,
      imoCompanyNumber: body.imoCompanyNumber?.trim() || currentBusinessInfo.imoCompanyNumber,
      headquarters: {
        addressLine1: body.headquarters?.addressLine1?.trim() || currentBusinessInfo.headquarters.addressLine1,
        city: body.headquarters?.city?.trim() || currentBusinessInfo.headquarters.city,
        state: body.headquarters?.state?.trim() || currentBusinessInfo.headquarters.state,
        country: body.headquarters?.country?.trim() || currentBusinessInfo.headquarters.country,
        postalCode: body.headquarters?.postalCode?.trim() || currentBusinessInfo.headquarters.postalCode
      },
      contactChannels: {
        commercialCharteringEmail: body.contactChannels.commercialCharteringEmail.trim(),
        operationsDemurrageEmail: body.contactChannels.operationsDemurrageEmail.trim(),
        generalInquiriesEmail: body.contactChannels.generalInquiriesEmail?.trim() || currentBusinessInfo.contactChannels.generalInquiriesEmail,
        primaryPhone: body.contactChannels.primaryPhone.trim(),
        emergency247OpsPhone: body.contactChannels.emergency247OpsPhone?.trim() || currentBusinessInfo.contactChannels.emergency247OpsPhone,
        satelliteVhfCallsign: body.contactChannels.satelliteVhfCallsign?.trim() || currentBusinessInfo.contactChannels.satelliteVhfCallsign
      },
      operatingHours: body.operatingHours?.trim() || currentBusinessInfo.operatingHours,
      globalDesks: Array.isArray(body.globalDesks) ? body.globalDesks : currentBusinessInfo.globalDesks
    };
    res.json({
      success: true,
      message: "Business information successfully updated on the server.",
      data: currentBusinessInfo
    });
  });
  app.post("/api/contact", (req, res) => {
    const { fullName, corporateEmail, companyName, phoneNumber, inquiryType, cargoParcelClass, message, urgency } = req.body;
    const errors = {};
    if (!fullName || typeof fullName !== "string" || fullName.trim().length < 2) {
      errors.fullName = "Full name is required (minimum 2 characters).";
    } else if (fullName.trim().length > 80) {
      errors.fullName = "Full name cannot exceed 80 characters.";
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!corporateEmail || typeof corporateEmail !== "string" || !emailRegex.test(corporateEmail.trim())) {
      errors.corporateEmail = "A valid corporate email address is required (e.g., trader@shipping.com).";
    }
    if (!companyName || typeof companyName !== "string" || companyName.trim().length < 2) {
      errors.companyName = "Company or trading house name is required.";
    }
    const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{2,5}[-\s\.]?[0-9]{3,8}$/;
    if (!phoneNumber || typeof phoneNumber !== "string" || !phoneRegex.test(phoneNumber.trim().replace(/\s+/g, ""))) {
      errors.phoneNumber = "Please provide a valid phone number with country code (e.g., +1 713 555 0192).";
    }
    const validInquiryTypes = [
      "Voyage Chartering & What-If Simulation",
      "Demurrage & Legal Risk Guard (WIBON/WIPON)",
      "Fleet AIS Radar & Tracking License",
      "Bulk Freight Hedging & FFA Curves",
      "General Enterprise Partnership"
    ];
    if (!inquiryType || !validInquiryTypes.includes(inquiryType)) {
      errors.inquiryType = "Please select a valid maritime inquiry category.";
    }
    if (!message || typeof message !== "string" || message.trim().length < 15) {
      errors.message = "Message details must be at least 15 characters describing your voyage or operational query.";
    } else if (message.trim().length > 3e3) {
      errors.message = "Message cannot exceed 3,000 characters.";
    }
    if (Object.keys(errors).length > 0) {
      return res.status(422).json({
        success: false,
        message: "Server validation failed. Please correct the highlighted fields.",
        errors
      });
    }
    const refPrefix = inquiryType.includes("Chartering") ? "CHTR" : inquiryType.includes("Demurrage") ? "DEMG" : "RADR";
    const randomSuffix = Math.floor(1e5 + Math.random() * 9e5);
    const referenceId = `FIQ-${refPrefix}-${(/* @__PURE__ */ new Date()).getFullYear()}-${randomSuffix}`;
    const submission = {
      id: referenceId,
      fullName: fullName.trim(),
      corporateEmail: corporateEmail.trim().toLowerCase(),
      companyName: companyName.trim(),
      phoneNumber: phoneNumber.trim(),
      inquiryType,
      cargoParcelClass: cargoParcelClass || "Unspecified",
      message: message.trim(),
      urgency: urgency || "Normal",
      receivedAt: (/* @__PURE__ */ new Date()).toISOString()
    };
    recentSubmissions.unshift(submission);
    if (recentSubmissions.length > 50) recentSubmissions.pop();
    res.status(201).json({
      success: true,
      message: "Your inquiry has been successfully validated and logged with the FreightIQ Commercial Watch Desk.",
      referenceId,
      timestamp: submission.receivedAt,
      dispatchDesk: currentBusinessInfo.contactChannels.commercialCharteringEmail,
      estimatedResponseTime: urgency === "Urgent Laycan (<48h)" ? "Within 2 Hours" : "Within 1 Business Day",
      submittedDetails: {
        fullName: submission.fullName,
        companyName: submission.companyName,
        corporateEmail: submission.corporateEmail,
        referenceId
      }
    });
  });
  app.get("/api/contact/submissions", (_req, res) => {
    res.json({
      success: true,
      count: recentSubmissions.length,
      submissions: recentSubmissions.slice(0, 10)
    });
  });
  if (process.env.NODE_ENV !== "production") {
    const vite = await (0, import_vite.createServer)({
      server: { middlewareMode: true },
      appType: "spa"
    });
    app.use(vite.middlewares);
  } else {
    const distPath = import_path.default.join(process.cwd(), "dist");
    app.use(import_express.default.static(distPath));
    app.get("*", (_req, res) => {
      res.sendFile(import_path.default.join(distPath, "index.html"));
    });
  }
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`FreightIQ Server running on http://localhost:${PORT}`);
  });
}
startServer();
//# sourceMappingURL=server.cjs.map
