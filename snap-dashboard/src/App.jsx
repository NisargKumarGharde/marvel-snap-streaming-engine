import { useState, useEffect } from "react";
import { Zap, BarChart2, Layers, TrendingUp, RefreshCw, AlertCircle } from "lucide-react";

const PLACEHOLDER = {
  total_matches: null,
  snap_rate: null,
  top_cards: null,
};

const MOCK_FALLBACK = {
  total_matches: 1284,
  snap_rate: 2.47,
  top_cards: { "Iron Man": 312, "Sera": 278, "Galactus": 241 },
};

function SkeletonBar({ w = "w-full" }) {
  return <div className={`h-3 rounded ${w} bg-gray-700 animate-pulse`} />;
}

function MetricCard({ icon: Icon, label, value, sub, loading, accent }) {
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gray-900 border border-gray-800 p-6 flex flex-col gap-3 shadow-xl`}>
      <div className={`absolute inset-0 opacity-10 bg-gradient-to-br ${accent}`} />
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-400">{label}</span>
        <div className={`p-2 rounded-xl bg-gradient-to-br ${accent} bg-opacity-20`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      {loading ? (
        <div className="flex flex-col gap-2 mt-1">
          <SkeletonBar w="w-2/3" />
          <SkeletonBar w="w-1/2" />
        </div>
      ) : (
        <>
          <div className="text-3xl font-extrabold text-white tracking-tight">{value}</div>
          {sub && <div className="text-xs text-gray-500">{sub}</div>}
        </>
      )}
    </div>
  );
}

function TopCardsCard({ cards, loading }) {
  const entries = cards ? Object.entries(cards).sort((a, b) => b[1] - a[1]).slice(0, 3) : [];
  const max = entries[0]?.[1] || 1;

  const rankColors = [
    "from-yellow-400 to-orange-500",
    "from-slate-300 to-slate-400",
    "from-amber-600 to-amber-700",
  ];

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gray-900 border border-gray-800 p-6 flex flex-col gap-4 shadow-xl">
      <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-purple-500 to-pink-600" />
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-400">Top 3 Played Cards</span>
        <div className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600">
          <Layers size={18} className="text-white" />
        </div>
      </div>
      {loading ? (
        <div className="flex flex-col gap-3 mt-1">
          {[1,2,3].map(i => (
            <div key={i} className="flex flex-col gap-1">
              <SkeletonBar w="w-1/3" />
              <SkeletonBar w={i === 1 ? "w-full" : i === 2 ? "w-3/4" : "w-1/2"} />
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col gap-3 mt-1">
          {entries.map(([name, count], i) => (
            <div key={name} className="flex flex-col gap-1">
              <div className="flex justify-between text-sm">
                <span className="font-semibold text-white flex items-center gap-2">
                  <span className={`text-xs font-bold bg-gradient-to-r ${rankColors[i]} bg-clip-text text-transparent`}>
                    #{i + 1}
                  </span>
                  {name}
                </span>
                <span className="text-gray-400 text-xs">{count.toLocaleString()} plays</span>
              </div>
              <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${rankColors[i]} transition-all duration-700`}
                  style={{ width: `${(count / max) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const cfg = {
    loading: { color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20", dot: "bg-yellow-400", label: "Fetching live data…" },
    live:    { color: "text-green-400 bg-green-400/10 border-green-400/20",  dot: "bg-green-400 animate-ping", label: "Live" },
    fallback:{ color: "text-orange-400 bg-orange-400/10 border-orange-400/20", dot: "bg-orange-400", label: "API unavailable — showing sample data" },
  };
  const c = cfg[status];
  return (
    <span className={`inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full border ${c.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(PLACEHOLDER);
  const [status, setStatus] = useState("loading"); // loading | live | fallback
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = async () => {
    setStatus("loading");
    setData(PLACEHOLDER);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/metrics", { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error("Non-2xx response");
      const json = await res.json();
      setData(json);
      setStatus("live");
    } catch {
      setData(MOCK_FALLBACK);
      setStatus("fallback");
    }
    setLastUpdated(new Date().toLocaleTimeString());
  };

  useEffect(() => { fetchData(); }, []);

  const loading = status === "loading";

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 md:p-10 font-sans">
      {/* Header */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="p-2 rounded-xl bg-gradient-to-br from-red-500 to-red-700 shadow-lg shadow-red-900/40">
              <Zap size={20} className="text-white" />
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-red-400 via-pink-300 to-purple-400 bg-clip-text text-transparent">
              Marvel Snap Analytics
            </h1>
          </div>
          <p className="text-gray-500 text-sm ml-12">Match intelligence dashboard</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={status} />
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-colors disabled:opacity-40"
          >
            <RefreshCw size={15} className={`text-gray-300 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        <MetricCard
          icon={BarChart2}
          label="Total Matches Analyzed"
          value={data.total_matches !== null ? data.total_matches.toLocaleString() : "—"}
          sub={lastUpdated ? `Last updated ${lastUpdated}` : undefined}
          loading={loading}
          accent="from-blue-500 to-cyan-500"
        />
        <MetricCard
          icon={TrendingUp}
          label="Average Snaps per Match"
          value={data.snap_rate !== null ? data.snap_rate.toFixed(2) : "—"}
          sub="Cubes doubled on average"
          loading={loading}
          accent="from-rose-500 to-pink-500"
        />
        <TopCardsCard cards={data.top_cards} loading={loading} />
      </div>

      {/* Footer */}
      <p className="text-center text-gray-700 text-xs mt-10">
        {status === "fallback" && (
          <span className="inline-flex items-center gap-1 text-orange-500/70">
            <AlertCircle size={11} /> Could not reach <code>127.0.0.1:8000/api/metrics</code> — displaying sample data.
          </span>
        )}
        {status === "live" && "✦ Data sourced from local API"}
        {status === "loading" && "Connecting to API…"}
      </p>
    </div>
  );
}