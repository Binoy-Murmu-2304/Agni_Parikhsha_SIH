import { useState, useEffect } from 'react';
import TopBar from '../components/TopBar';
import FleetSummaryStrip from '../components/FleetSummaryStrip';
import LotSelector from '../components/LotSelector';
import KanbanBoard from '../components/KanbanBoard';
import LotSummaryStrip from '../components/LotSummaryStrip';
import DrillDownPanel from '../components/DrillDownPanel';
import ResultsMetricsTab from '../components/ResultsMetricsTab';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [lots, setLots] = useState([]);
  const [selectedLotId, setSelectedLotId] = useState('ALL');
  const [lotComponents, setLotComponents] = useState([]);
  const [lotSummary, setLotSummary] = useState(null);
  const [selectedComp, setSelectedComp] = useState(null);
  const [cardData, setCardData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [dispositionFilter, setDispositionFilter] = useState(null);
  const [activeTab, setActiveTab] = useState('triage');
  const [loadingScreen, setLoadingScreen] = useState(false);
  const [loadingComponents, setLoadingComponents] = useState(false);
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingZip, setLoadingZip] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // 7. Download PDF Screening Report (Lot or Fleet)
  const handleDownloadReport = (targetId) => {
    setLoadingReport(true);
    const reportUrl = API_URL + `/lots/${targetId}/report`;
    const link = document.createElement('a');
    link.href = reportUrl;
    const isFleet = targetId.toLowerCase() === 'all' || targetId.toLowerCase() === 'fleet';
    link.download = isFleet
      ? `AGNI_PARIKSHA_FLEET_REPORT_2026-09-24.pdf`
      : `AGNI_PARIKSHA_LOT_REPORT_${targetId}_2026-09-24.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => setLoadingReport(false), 1200);
  };

  // 1. Fetch metrics & lots list on startup
  useEffect(() => {
    fetch(API_URL + '/metrics')
      .then(r => r.json())
      .then(setMetrics)
      .catch(err => console.error("Failed to fetch metrics:", err));

    fetch(API_URL + '/lots')
      .then(r => r.json())
      .then(data => {
        setLots(data);
      })
      .catch(err => console.error("Failed to fetch lots inventory:", err));
  }, []);

  // 2. Select lot (or 'ALL') and fetch components & summary for single lot mode
  const handleSelectLot = async (lotId) => {
    setSelectedLotId(lotId);
    setErrorMsg(null);

    if (lotId === 'ALL') {
      setLotComponents([]);
      setLotSummary(null);
      return;
    }

    setLoadingComponents(true);

    try {
      const compRes = await fetch(API_URL + `/lots/${lotId}/components?page=1&per_page=5000`);
      if (compRes.ok) {
        const compData = await compRes.json();
        setLotComponents(compData.components || []);
        if (compData.components && compData.components.length > 0) {
          loadComponentDetails(compData.components[0]);
        }
      }

      const sumRes = await fetch(API_URL + `/lots/${lotId}/summary`);
      if (sumRes.ok) {
        setLotSummary(await sumRes.json());
      }
    } catch (err) {
      console.error("handleSelectLot error:", err);
      setErrorMsg(`Failed to load data for lot ${lotId}`);
    } finally {
      setLoadingComponents(false);
    }
  };

  // 3. Load Component Details
  const loadComponentDetails = async (compObj) => {
    setErrorMsg(null);
    const compId = typeof compObj === 'string' ? compObj : compObj.component_id;

    try {
      const res = await fetch(API_URL + '/components/' + compId);
      if (res.ok) {
        const comp = await res.json();
        const merged = typeof compObj === 'object' ? { ...compObj, ...comp } : comp;
        setSelectedComp(merged);
      } else if (typeof compObj === 'object') {
        setSelectedComp(compObj);
      }

      const cardRes = await fetch(API_URL + '/components/' + compId + '/card');
      if (cardRes.ok) {
        const card = await cardRes.json();
        setCardData(card);
      } else {
        setCardData(null);
      }
    } catch (err) {
      console.error("loadComponentDetails error:", err);
      if (typeof compObj === 'object') setSelectedComp(compObj);
    }
  };

  // 4. Secondary Action: Live Screening endpoint (POST /lots/screen)
  const handleScreenCustomLot = async () => {
    setErrorMsg(null);
    setLoadingScreen(true);
    try {
      const demoPayload = [
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_001",
          "family": "DIGITAL_IC",
          "value_0h": 10.0,
          "value_24h": 10.1,
          "is_defective": 0,
          "mechanism": "NONE"
        },
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_002",
          "family": "DIGITAL_IC",
          "value_0h": 10.0,
          "value_24h": 16.5,
          "is_defective": 1,
          "mechanism": "THIN_OXIDE_BREAKDOWN"
        },
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_003",
          "family": "MIXED_SIGNAL_IC",
          "value_0h": 2.0,
          "value_24h": 2.05,
          "is_defective": 0,
          "mechanism": "NONE"
        },
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_004",
          "family": "PRECISION_VOLTAGE_REF",
          "value_0h": 5.0,
          "value_24h": 5.8,
          "is_defective": 1,
          "mechanism": "DRIFT"
        },
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_005",
          "family": "MEMS_GYROSCOPE",
          "value_0h": 1.2,
          "value_24h": 1.21,
          "is_defective": 0,
          "mechanism": "NONE"
        },
        {
          "lot_id": "LOT_SCREEN_DEMO",
          "component_id": "SCREEN_IC_006",
          "family": "IMAGE_SENSOR",
          "value_0h": 3.0,
          "value_24h": 3.02,
          "is_defective": 0,
          "mechanism": "NONE"
        }
      ];

      const res = await fetch(API_URL + '/lots/screen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(demoPayload)
      });
      if (!res.ok) throw new Error("Custom lot screening failed");

      const responseArray = await res.json();
      setSelectedLotId("LOT_SCREEN_DEMO");
      setLotComponents(responseArray);

      const greenCount = responseArray.filter(c => c.disposition === 'GREEN').length;
      const burnInCount = responseArray.filter(c => c.disposition === 'FULL_BURN_IN').length;
      const redCount = responseArray.filter(c => c.disposition === 'RED').length;
      const total = responseArray.length;
      const greenFraction = total > 0 ? greenCount / total : 0;
      const realizedSavings = Number((greenFraction * 85.71).toFixed(2));

      setLotSummary({
        lot_id: "LOT_SCREEN_DEMO",
        counts: { GREEN: greenCount, FULL_BURN_IN: burnInCount, RED: redCount },
        total: total,
        green_count: greenCount,
        green_fraction: Number(greenFraction.toFixed(4)),
        realized_savings: realizedSavings,
        yield_assumption: `Based on custom screened lot defect rate (${(greenFraction * 100).toFixed(1)}% GREEN yield)`
      });

      if (responseArray.length > 0) {
        loadComponentDetails(responseArray[0]);
      }

      const lotsRes = await fetch(API_URL + '/lots');
      if (lotsRes.ok) {
        setLots(await lotsRes.json());
      }
    } catch (err) {
      console.error("handleScreenCustomLot error:", err);
      setErrorMsg("ERROR :: POST /lots/screen custom lot path failed.");
    } finally {
      setLoadingScreen(false);
    }
  };

  // 5. Download PDF Certificate
  const handleDownloadPdf = (compId) => {
    setLoadingPdf(true);
    const pdfUrl = API_URL + `/components/${compId}/certificate`;
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = `AGNI_PARIKSHA_${compId}_certificate.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => setLoadingPdf(false), 800);
  };

  // 6. Export Lot Certificates ZIP
  const handleExportZip = (lotId) => {
    setLoadingZip(true);
    const zipUrl = API_URL + `/lots/${lotId}/certificates`;
    const link = document.createElement('a');
    link.href = zipUrl;
    link.download = `AGNI_PARIKSHA_${lotId}_certificates.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => setLoadingZip(false), 1200);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-main)' }}>
      {/* Top Bar Navigation */}
      <TopBar activeTab={activeTab} setActiveTab={setActiveTab} commitHash="c86c4b28" />

      {/* Main Container */}
      <main style={{ flex: 1, padding: '12px 16px', margin: '0 auto', width: '100%', maxWidth: '1600px' }}>
        {errorMsg && (
          <div style={{ padding: '6px 10px', border: '1px solid #ff1744', color: '#ff1744', marginBottom: '12px', fontSize: '11px' }}>
            ERROR :: {errorMsg}
          </div>
        )}

        {/* Tab 1: Triage Board */}
        {activeTab === 'triage' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '16px', alignItems: 'start', width: '100%', minWidth: 0 }}>
            {/* Left Side: Three Triage Zones */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minWidth: 0, width: '100%' }}>
              {/* ZONE 1: FLEET SUMMARY (compact, one line) */}
              <FleetSummaryStrip
                lots={lots}
                dispositionFilter={dispositionFilter}
                onSelectDispositionFilter={setDispositionFilter}
              />

              {/* ZONE 2: LOT SELECTOR (horizontal scrollable row) + Screen Action */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', minWidth: 0, width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', minWidth: 0 }}>
                  <span style={{ fontSize: '11px', color: '#4ea1f0', fontWeight: 'bold', letterSpacing: '1px', textTransform: 'uppercase' }}>
                    LOT INVENTORY CONSOLE
                  </span>
                  <button
                    className="btn-secondary"
                    onClick={handleScreenCustomLot}
                    disabled={loadingScreen}
                    style={{ fontSize: '10px', padding: '2px 6px' }}
                  >
                    {loadingScreen ? "SCREENING LOT..." : "[SCREEN CUSTOM LOT (POST /lots/screen)]"}
                  </button>
                </div>

                <LotSelector
                  lots={lots}
                  selectedLotId={selectedLotId}
                  onSelectLot={handleSelectLot}
                />
              </div>

              {/* ZONE 3: TRIAGE KANBAN (three columns) */}
              <div style={{ width: '100%', minWidth: 0 }}>
                <KanbanBoard
                  selectedLotId={selectedLotId}
                  lotComponents={lotComponents}
                  selectedComp={selectedComp}
                  onSelectComponent={loadComponentDetails}
                  onSelectLot={handleSelectLot}
                  searchQuery={searchQuery}
                  setSearchQuery={setSearchQuery}
                  isLoading={loadingComponents || loadingScreen}
                  dispositionFilter={dispositionFilter}
                  setDispositionFilter={setDispositionFilter}
                />
              </div>

              {/* Lot Summary Strip with PDF Report & ZIP Export Buttons */}
              <LotSummaryStrip
                lotSummary={lotSummary}
                lotId={selectedLotId}
                lots={lots}
                metrics={metrics}
                onExportZip={handleExportZip}
                loadingZip={loadingZip}
                onDownloadReport={handleDownloadReport}
                loadingReport={loadingReport}
              />
            </div>

            {/* Right Side: DRILL-DOWN Panel (380px) */}
            <div>
              <DrillDownPanel
                selectedComp={selectedComp}
                cardData={cardData}
                onClose={() => setSelectedComp(null)}
                onDownloadPdf={handleDownloadPdf}
                loadingPdf={loadingPdf}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Results & Metrics */}
        {activeTab === 'results' && (
          <ResultsMetricsTab metrics={metrics} />
        )}
      </main>
    </div>
  );
}

