

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function formatNumber(value) {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "—";
  }
  return new Intl.NumberFormat("en-GB", {
    maximumFractionDigits: 1,
  }).format(value);
}

function formatTime(value) {
  return new Date(value).toLocaleTimeString("en-GB", {
    timeZone: "UTC",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function MetricCard({ label, value, description, tone = "" }) {
  return (
    <article className="metric-card">
      <p className="metric-label">{label}</p>
      <p className={`metric-value ${tone}`}>{value}</p>
      <p className="metric-description">{description}</p>
    </article>
  );
}
function validateDecisionDate(value) {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return "Please enter a valid date.";
  }

  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));

  // Reject impossible dates, such as 30 February.
  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    return "Invalid date. Please check the day, month, and year.";
  }

  if (year !== 2026 || month !== 1 || day < 1 || day > 31) {
    return "Please enter a date between 1 January and 31 January 2026.";
  }

  return "";
}
export default function App() {
  const [decisionDate, setDecisionDate] = useState("2026-01-15");
  const [cutoffHour, setCutoffHour] = useState("10");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

  async function loadAnalysis() {
    const validationError = validateDecisionDate(decisionDate);

const deliveryDate =
  !validationError && decisionDate
    ? (() => {
        const date = new Date(`${decisionDate}T12:00:00`);
        date.setDate(date.getDate() + 1);
        return date.toISOString().slice(0, 10);
      })()
    : "";
   try {
        const params = new URLSearchParams({
          date: decisionDate,
          cutoff_hour: cutoffHour,
        });

        const response = await fetch(
          `${API_URL}/api/analysis?${params.toString()}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(
            body.detail || `Request failed with status ${response.status}`
          );
        }

        const result = await response.json();
        setAnalysis(result);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadAnalysis();
    return () => controller.abort();
  }, [decisionDate, cutoffHour]);

  const chartData = (analysis?.periods || []).map((period) => ({
    ...period,
    timeLabel: formatTime(period.startTime),
  }));

  const metrics = analysis?.metrics;

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Wind Monitor home">
          <span className="brand-mark">W</span>
          <span>Wind<span className="brand-light">Monitor</span></span>
        </a>
        <span className="header-tag">
          <span className="status-dot" />
          UK WIND ANALYTICS
        </span>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">FORECAST INTELLIGENCE / GREAT BRITAIN</p>
          <h1>Wind Forecast Monitor</h1>
          <p className="subtitle">
            Compare forecast wind generation against actual output to understand
            forecast accuracy before delivery.
          </p>
        </div>
        <div className="data-source">
          <span className="source-icon">↗</span>
          <span>
            <strong>Elexon BMRS</strong>
            <small>Historical market data</small>
          </span>
        </div>
      </section>

      <section className="filter-panel">
        <div className="filter-heading">
          <div>
            <h2>Analysis settings</h2>
            <p>Choose a decision date and forecast cutoff.</p>
          </div>
          <span className="period-tag">JANUARY 2026</span>
        </div>

        <div className="filters">
          <label className="field">
            <span>Decision date</span>
            <input
  type="date"
  min="2026-01-01"
  max="2026-01-31"
  value={decisionDate}
  onChange={(event) => {
  const value = event.target.value;
  setDecisionDate(value);

  const validationError = validateDecisionDate(value);
  setError(validationError);

  if (validationError) {
    setAnalysis(null);
  }
}}

/>
          </label>

          <label className="field">
            <span>Forecast cutoff (UK time)</span>
            <select
              value={cutoffHour}
              onChange={(event) => setCutoffHour(event.target.value)}
            >
              {Array.from({ length: 24 }, (_, hour) => (
                <option key={hour} value={hour}>
                  {String(hour).padStart(2, "0")}:00
                </option>
              ))}
            </select>
          </label>
<div className="delivery-info">
  <span>DELIVERY DATE</span>
  <strong>{analysis?.deliveryDate || "—"}</strong>
</div>
          
        </div>
      </section>

      {loading && (
        <div className="notice loading-notice">
          <span className="spinner" />
          Loading historical wind data…
        </div>
      )}

      {error && (
        <div className="notice error-notice">
          <strong>Unable to load analysis</strong>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && analysis && (
        <>
          <section className="section-heading">
            <div>
              <h2>Performance overview</h2>
              <p>
                Decision on {analysis.decisionDate} · Delivery on{" "}
                {analysis.deliveryDate} · Cutoff {String(analysis.cutoffHourUK).padStart(2, "0")}:00 UK time
              </p>
            </div>
            <span className="matched-tag">
              {analysis.matchedPeriods} matched hourly periods
            </span>
          </section>

          <section className="metrics-grid">
            <MetricCard
              label="Mean absolute error"
              value={formatNumber(metrics?.mae)}
              description="Average absolute forecast error"
            />
            <MetricCard
              label="Root mean squared error"
              value={formatNumber(metrics?.rmse)}
              description="Penalizes larger errors"
            />
            <MetricCard
              label="Forecast bias"
              value={metrics?.bias == null
                ? "—"
                : `${metrics.bias > 0 ? "+" : ""}${formatNumber(metrics.bias)}`}
              description={
                metrics?.bias > 0
                  ? "Forecast was higher than actual on average"
                  : metrics?.bias < 0
                    ? "Forecast was lower than actual on average"
                    : "Average forecast and actual were aligned"
              }
              tone={
                metrics?.bias > 0
                  ? "positive"
                  : metrics?.bias < 0
                    ? "negative"
                    : ""
              }
            />
          </section>

          <section className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <h2>Forecast vs actual generation</h2>
                <p>Hourly wind generation · values as returned by Elexon</p>
              </div>
              <div className="chart-legend-note">
                <span className="legend-line forecast-line" /> Forecast
                <span className="legend-line actual-line" /> Actual
              </div>
            </div>

            {chartData.length > 0 ? (
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={chartData}
                    margin={{ top: 16, right: 18, left: 4, bottom: 4 }}
                  >
                    <CartesianGrid stroke="#e9edf3" strokeDasharray="4 4" />
                    <XAxis
                      dataKey="timeLabel"
                      tick={{ fill: "#748094", fontSize: 12 }}
                      tickLine={false}
                      axisLine={{ stroke: "#dfe5ed" }}
                      minTickGap={22}
                    />
                    <YAxis
                      tick={{ fill: "#748094", fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => formatNumber(value)}
                      width={65}
                    />
                    <Tooltip
                      labelFormatter={(label) => `Time: ${label} UTC`}
                      formatter={(value, name) => [
                        formatNumber(value),
                        name === "forecast" ? "Forecast" : "Actual",
                      ]}
                      contentStyle={{
                        border: "1px solid #e1e7ef",
                        borderRadius: 10,
                        boxShadow: "0 8px 24px #17243b12",
                      }}
                    />
                    <Legend
                      formatter={(value) =>
                        value === "forecast" ? "Forecast" : "Actual"
                      }
                    />
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      name="forecast"
                      stroke="#3569d4"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      name="actual"
                      stroke="#159b82"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="empty-state">No matched periods are available for this selection.</p>
            )}

            <p className="chart-footnote">
              Times are shown in UTC. Forecast and actual values are compared
              only where their timestamps match.
            </p>
          </section>

          <section className="panel table-panel">
            <div className="panel-heading">
              <div>
                <h2>Hourly breakdown</h2>
                <p>Forecast publication, actual output, and signed error</p>
              </div>
              <span className="table-count">
                {analysis.periods.length} rows
              </span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Hour (UTC)</th>
                    <th>Published (UTC)</th>
                    <th>Forecast</th>
                    <th>Actual</th>
                    <th>Error</th>
                    <th>Absolute error</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.periods.map((period) => (
                    <tr key={period.startTime}>
                      <td className="time-cell">{formatTime(period.startTime)}</td>
                      <td>{new Date(period.publishTime).toLocaleString("en-GB", {
                        timeZone: "UTC",
                        day: "2-digit",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false,
                      })}</td>
                      <td>{formatNumber(period.forecast)}</td>
                      <td>{formatNumber(period.actual)}</td>
                      <td className={
                        period.error > 0
                          ? "error-positive"
                          : period.error < 0
                            ? "error-negative"
                            : ""
                      }>
                        {period.error > 0 ? "+" : ""}
                        {formatNumber(period.error)}
                      </td>
                      <td>{formatNumber(period.absoluteError)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      <footer className="footer">
        <span>Wind Forecast Monitor</span>
        <span>Data source: Elexon BMRS · January 2026 analysis</span>
        <span>Forecast − actual = error</span>
      </footer>
    </main>
  );
}
