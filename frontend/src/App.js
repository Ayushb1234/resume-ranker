import React, { useState } from "react";
import ResultCard from "./components/ResultCard";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(10);
  const [weight, setWeight] = useState(0.5);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file || !jd) {
      alert("Attach zip and provide job description");
      return;
    }
    const fd = new FormData();
    fd.append("resumes_zip", file);
    fd.append("job_description", jd);
    fd.append("top_k", topK);
    fd.append("skill_vs_exp_weight", weight);

    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/rank`, {
        method: "POST",
        body: fd,
      });
      const data = await resp.json();
      setResults(data);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Resume Ranker — demo</h1>
      <form onSubmit={onSubmit} className="form">
        <label>Upload resumes (.zip)</label>
        <input type="file" accept=".zip" onChange={(e) => setFile(e.target.files[0])} />
        <label>Job Description</label>
        <textarea rows={8} value={jd} onChange={(e) => setJd(e.target.value)} />
        <div className="controls">
          <label>Top K</label>
          <input type="number" value={topK} onChange={(e) => setTopK(e.target.value)} min={1} max={50} />
          <label>Skill vs Exp weight (0-1)</label>
          <input type="number" step="0.1" min="0" max="1" value={weight} onChange={(e) => setWeight(e.target.value)} />
        </div>
        <button type="submit" disabled={loading}>{loading ? "Ranking..." : "Rank"}</button>
      </form>

      <div className="results">
        {results ? (
          <>
            <h2>Job skills detected: {results.job_skills && results.job_skills.join(", ")}</h2>
            {results.results && results.results.length === 0 && <p>No candidates found.</p>}
            {results.results && results.results.map((r) => <ResultCard key={r.candidate_id} result={r} />)}
            <pre className="raw">{JSON.stringify(results, null, 2)}</pre>
          </>
        ) : (
          <p>No results yet — upload resumes zip + JD and hit Rank.</p>
        )}
      </div>
    </div>
  );
}

export default App;
