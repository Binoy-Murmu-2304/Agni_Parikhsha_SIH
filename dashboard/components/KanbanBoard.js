import React, { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const ROUTED_FAMILIES = ["DIGITAL_IC", "MIXED_SIGNAL_IC", "PRECISION_VOLTAGE_REF"];

const ROUTED_EMPTY_MESSAGES = {
  GREEN: "0 — All parts in this family are routed to 168h burn-in (capability routing: family MAE > 20% of spec max)",
  FULL_BURN_IN: "All parts in this family awaiting 168h burn-in certification",
  RED: "0 — All parts in this family are routed to 168h burn-in (early rejection is overridden by routing policy)"
};

const CAPABLE_EMPTY_MESSAGES = {
  GREEN: "No clean parts in this batch",
  FULL_BURN_IN: "No uncertain parts in this batch",
  RED: "No defects detected in this batch"
};

const FAMILIES = [
  { id: 'ALL', label: 'ALL' },
  { id: 'DIGITAL_IC', label: 'DIGITAL_IC' },
  { id: 'MIXED_SIGNAL_IC', label: 'MIXED_SIGNAL' },
  { id: 'MEMS_GYROSCOPE', label: 'MEMS_GYRO' },
  { id: 'PRECISION_VOLTAGE_REF', label: 'PRECISION_REF' },
  { id: 'IMAGE_SENSOR', label: 'IMAGE_SENSOR' }
];

export default function KanbanBoard({
  selectedLotId = 'ALL',
  lotComponents = [],
  selectedComp,
  onSelectComponent,
  onSelectLot,
  searchQuery,
  setSearchQuery,
  isLoading,
  dispositionFilter,
  setDispositionFilter
}) {
  const isAllLots = selectedLotId === 'ALL';
  const [selectedFamily, setSelectedFamily] = useState('ALL');

  // ALL LOTS state for paginated columns
  const [allLotsState, setAllLotsState] = useState({
    GREEN: { items: [], page: 1, total: 0, loading: false },
    FULL_BURN_IN: { items: [], page: 1, total: 0, loading: false },
    RED: { items: [], page: 1, total: 0, loading: false }
  });

  // Fetch initial page 1 for each column when in ALL LOTS mode
  useEffect(() => {
    if (!isAllLots) return;

    let isMounted = true;
    const fetchColumn = async (disp) => {
      try {
        setAllLotsState(prev => ({
          ...prev,
          [disp]: { ...prev[disp], loading: true }
        }));

        const params = new URLSearchParams({
          disposition: disp,
          page: '1',
          per_page: '50'
        });
        if (selectedFamily && selectedFamily !== 'ALL') {
          params.append('family', selectedFamily);
        }
        if (searchQuery) {
          params.append('search', searchQuery);
        }

        const res = await fetch(`${API_URL}/components/all?${params.toString()}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setAllLotsState(prev => ({
              ...prev,
              [disp]: {
                items: data.components || [],
                page: 1,
                total: data.total || 0,
                loading: false
              }
            }));
          }
        }
      } catch (err) {
        console.error(`Failed to fetch ALL LOTS column ${disp}:`, err);
        if (isMounted) {
          setAllLotsState(prev => ({
            ...prev,
            [disp]: { ...prev[disp], loading: false }
          }));
        }
      }
    };

    fetchColumn('GREEN');
    fetchColumn('FULL_BURN_IN');
    fetchColumn('RED');

    return () => { isMounted = false; };
  }, [isAllLots, selectedFamily, searchQuery]);

  // Handle Load 50 More for a column in ALL LOTS mode
  const handleLoadMore = async (disp) => {
    const colState = allLotsState[disp];
    if (colState.loading) return;

    const nextPage = colState.page + 1;
    setAllLotsState(prev => ({
      ...prev,
      [disp]: { ...prev[disp], loading: true }
    }));

    try {
      const params = new URLSearchParams({
        disposition: disp,
        page: String(nextPage),
        per_page: '50'
      });
      if (selectedFamily && selectedFamily !== 'ALL') {
        params.append('family', selectedFamily);
      }
      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const res = await fetch(`${API_URL}/components/all?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        const newItems = data.components || [];
        setAllLotsState(prev => ({
          ...prev,
          [disp]: {
            items: [...prev[disp].items, ...newItems],
            page: nextPage,
            total: data.total || prev[disp].total,
            loading: false
          }
        }));
      }
    } catch (err) {
      console.error(`Failed to load more for ${disp}:`, err);
      setAllLotsState(prev => ({
        ...prev,
        [disp]: { ...prev[disp], loading: false }
      }));
    }
  };

  // Single Lot Mode filtering
  const componentsList = Array.isArray(lotComponents) ? lotComponents : [];
  const currentFamily = componentsList.length > 0 ? componentsList[0].family : null;
  const isRoutedFamily = currentFamily ? ROUTED_FAMILIES.includes(currentFamily) : false;

  const singleLotFiltered = componentsList.filter(c => {
    if (selectedFamily && selectedFamily !== 'ALL' && c.family !== selectedFamily) {
      return false;
    }
    if (searchQuery && c.component_id && !c.component_id.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const greenCompsSingle = singleLotFiltered.filter(c => c.disposition === 'GREEN');
  const amberCompsSingle = singleLotFiltered.filter(c => c.disposition === 'FULL_BURN_IN');
  const redCompsSingle = singleLotFiltered.filter(c => c.disposition === 'RED');

  const getColumnData = (colKey) => {
    if (isAllLots) {
      const colState = allLotsState[colKey] || { items: [], page: 1, total: 0, loading: false };
      return {
        items: colState.items,
        total: colState.total,
        loading: colState.loading,
        hasMore: colState.items.length < colState.total
      };
    } else {
      const map = { GREEN: greenCompsSingle, FULL_BURN_IN: amberCompsSingle, RED: redCompsSingle };
      const items = map[colKey] || [];
      return {
        items: items,
        total: items.length,
        loading: isLoading,
        hasMore: false
      };
    }
  };

  const renderColumn = (colKey, defaultTitle, statusClass, headerColor) => {
    if (dispositionFilter && dispositionFilter !== colKey) {
      return null;
    }

    const { items, total, loading, hasMore } = getColumnData(colKey);
    const isRoutedEmpty = !isAllLots && isRoutedFamily && (colKey === 'GREEN' || colKey === 'RED') && items.length === 0;
    const emptyText = isAllLots
      ? `No components found in ${colKey} tier for current filters`
      : isRoutedFamily
      ? ROUTED_EMPTY_MESSAGES[colKey]
      : CAPABLE_EMPTY_MESSAGES[colKey];

    let title = defaultTitle;
    if (isAllLots) {
      if (colKey === 'GREEN') title = "GREEN — EARLY EXIT (PASS)";
      else if (colKey === 'FULL_BURN_IN') title = "FULL_BURN_IN — ROUTE TO 168H";
      else if (colKey === 'RED') title = "RED — REJECT";
    }

    return (
      <div
        className="kanban-column col"
        style={{
          minWidth: 0,
          width: '100%',
          overflowX: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          boxSizing: 'border-box'
        }}
      >
        {/* Compact Column Header */}
        <div
          className={`column-header col-header ${headerColor}`}
          style={{
            minWidth: 0,
            width: '100%',
            overflow: 'hidden',
            boxSizing: 'border-box'
          }}
        >
          <span
            title={title}
            style={{
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              minWidth: 0,
              flex: 1
            }}
          >
            {title}
          </span>
          <span className="mono-num" style={{ flexShrink: 0, marginLeft: '4px', color: headerColor === 'green' ? '#00e676' : headerColor === 'amber' ? '#ffab00' : '#ff1744' }}>
            ({total})
          </span>
        </div>

        <div
          className="kanban-card-list col-cards"
          style={{
            minWidth: 0,
            width: '100%',
            overflowY: 'auto',
            maxHeight: '60vh',
            overflowX: 'hidden',
            boxSizing: 'border-box'
          }}
        >
          {loading && items.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '10px', fontSize: '10px', color: '#6b7280', minWidth: 0 }}>
              LOADING...
            </div>
          ) : items.length === 0 ? (
            <div
              style={{
                minHeight: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                padding: '10px',
                fontSize: '10px',
                color: isRoutedEmpty ? '#ffab00' : '#6b7280',
                minWidth: 0,
                width: '100%',
                boxSizing: 'border-box'
              }}
            >
              <p style={{ lineHeight: '1.3', margin: 0, minWidth: 0, width: '100%', wordBreak: 'break-word', overflowWrap: 'anywhere' }}>
                {emptyText}
              </p>
            </div>
          ) : (
            <>
              {items.map(comp => {
                const isSelected = selectedComp && selectedComp.component_id === comp.component_id;

                let rawTier = comp.risk_tier ? String(comp.risk_tier).toUpperCase() : '';
                if (!rawTier || rawTier === 'NAN' || rawTier === 'NULL' || rawTier === 'UNDEFINED') {
                  rawTier = comp.disposition === 'RED' ? 'HIGH' : comp.disposition === 'FULL_BURN_IN' ? 'MEDIUM' : comp.disposition === 'GREEN' ? 'LOW' : 'UNKNOWN';
                }

                const riskTextClass = rawTier === 'HIGH' ? 'text-risk-high' : rawTier === 'MEDIUM' ? 'text-risk-medium' : rawTier === 'LOW' ? 'text-risk-low' : 'text-risk-unknown';

                const unit = comp.unit || '';
                const predVal = comp.pred_168h !== null && comp.pred_168h !== undefined
                  ? Number(comp.pred_168h).toFixed(1)
                  : null;
                const predStr = predVal !== null
                  ? `${predVal} ${unit}`
                  : '—';

                const lotBadgeText = comp.lot_id ? comp.lot_id.replace('FINAL_', '') : '';

                return (
                  <div
                    key={`${comp.lot_id}_${comp.component_id}`}
                    className={`component-card ${statusClass} ${isSelected ? 'selected' : ''}`}
                    onClick={() => onSelectComponent(comp)}
                  >
                    {/* Row 1 */}
                    <div className="row1">
                      <span className="comp-id">
                        {comp.component_id}
                      </span>
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'center', flexShrink: 0 }}>
                        <span className="family-chip">
                          {comp.family || 'IC'}
                        </span>
                        {comp.trigger_module_a === 1 && (
                          <span className="trigger-tag-red">
                            MOD_A
                          </span>
                        )}
                        {comp.trigger_safety_slope === 1 && (
                          <span className="trigger-tag-red">
                            SAFETY_SLOPE
                          </span>
                        )}

                        {/* Lot Badge (in ALL LOTS mode) */}
                        {isAllLots && comp.lot_id && (
                          <span
                            onClick={(e) => {
                              e.stopPropagation();
                              if (onSelectLot) onSelectLot(comp.lot_id);
                            }}
                            title={`Click to view lot ${comp.lot_id}`}
                            style={{
                              fontSize: '9px',
                              color: '#4ea1f0',
                              border: '1px solid #1e1e2e',
                              padding: '0px 3px',
                              cursor: 'pointer',
                              marginLeft: '2px',
                              borderRadius: '0px'
                            }}
                          >
                            [{lotBadgeText}]
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Row 2 */}
                    <div className="row2">
                      <span className={riskTextClass}>
                        {rawTier}
                      </span>
                      <span style={{ fontSize: '11px', color: '#c8ccd4' }}>
                        {predStr}
                      </span>
                    </div>
                  </div>
                );
              })}

              {/* Pagination "LOAD 50 MORE" for ALL LOTS mode */}
              {isAllLots && hasMore && (
                <div style={{ padding: '6px 8px', textAlign: 'center', borderTop: '1px solid #1e1e2e', marginTop: '4px' }}>
                  <button
                    className="btn-secondary"
                    onClick={() => handleLoadMore(colKey)}
                    disabled={loading}
                    style={{ fontSize: '10px', width: '100%', padding: '4px' }}
                  >
                    {loading ? "LOADING..." : "LOAD 50 MORE"}
                  </button>
                  <div style={{ fontSize: '9px', color: '#6b7280', marginTop: '2px' }}>
                    Showing {items.length} of {total} — Load more
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%' }}>
      {/* Contextual Banner Above Kanban */}
      {isAllLots ? (
        <div
          style={{
            padding: '3px 6px',
            border: '1px solid #4ea1f0',
            color: '#4ea1f0',
            fontSize: '10px',
            lineHeight: '1.3'
          }}
        >
          <strong>[FLEET-WIDE AGGREGATE VIEW]</strong> — Showing components triaged across all 31 lots. Filter by family or click any <code>[LOT_xxxx]</code> badge on a card to inspect an individual lot.
        </div>
      ) : isRoutedFamily ? (
        <div
          style={{
            padding: '3px 6px',
            border: '1px solid #ffab00',
            color: '#ffab00',
            fontSize: '10px',
            lineHeight: '1.3'
          }}
        >
          <strong>[!] ROUTED FAMILY ({currentFamily})</strong> — MAE &gt; 20% spec max. Mandatory 168h burn-in required for all components. Select MEMS_GYROSCOPE or IMAGE_SENSOR for multi-tier triage.
        </div>
      ) : (
        <div
          style={{
            padding: '3px 6px',
            border: '1px solid #00e676',
            color: '#00e676',
            fontSize: '10px',
            lineHeight: '1.3'
          }}
        >
          <strong>[PASS] CAPABLE FAMILY ({currentFamily || 'ACTIVE'})</strong> — MAE &le; 20% spec max. 24h exit enabled for GREEN tier.
        </div>
      )}

      {/* FAMILY FILTER ROW */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflowX: 'auto', paddingBottom: '2px' }}>
        <span style={{ fontSize: '10px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', flexShrink: 0 }}>
          FAMILY:
        </span>
        {FAMILIES.map(f => {
          const isActive = selectedFamily === f.id;
          return (
            <button
              key={f.id}
              onClick={() => setSelectedFamily(f.id)}
              style={{
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid #4ea1f0' : '2px solid transparent',
                color: isActive ? '#4ea1f0' : '#6b7280',
                fontWeight: isActive ? '600' : 'normal',
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                padding: '2px 4px',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                textTransform: 'uppercase'
              }}
            >
              [{f.label}]
            </button>
          );
        })}
      </div>

      {/* Search Input & Active Disposition Filter Banner */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <input
          type="text"
          placeholder="FILTER COMPONENTS BY ID OR LOT..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            flex: 1,
            padding: '2px 6px',
            background: '#0a0a0f',
            border: '1px solid #1e1e2e',
            color: '#c8ccd4',
            fontSize: '10px'
          }}
        />
        {searchQuery && (
          <button className="btn-secondary" onClick={() => setSearchQuery('')} style={{ fontSize: '9px', padding: '1px 4px' }}>CLEAR SEARCH</button>
        )}
        {dispositionFilter && (
          <button
            className="btn-secondary"
            onClick={() => setDispositionFilter && setDispositionFilter(null)}
            style={{ fontSize: '9px', padding: '1px 4px', color: '#ffab00', borderColor: '#ffab00' }}
          >
            [CLEAR DISPOSITION FILTER: {dispositionFilter}]
          </button>
        )}
      </div>

      {/* 3 Kanban Columns */}
      <div
        className="kanban-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: dispositionFilter ? '1fr' : '1fr 1fr 1fr',
          width: '100%',
          gap: 0,
          minWidth: 0,
          boxSizing: 'border-box'
        }}
      >
        {renderColumn("GREEN", "GREEN — EARLY EXIT", "green", "green")}
        {renderColumn("FULL_BURN_IN", "FULL_BURN_IN — ROUTE TO 168H", "amber", "amber")}
        {renderColumn("RED", "RED — REJECT", "red", "red")}
      </div>
    </div>
  );
}
