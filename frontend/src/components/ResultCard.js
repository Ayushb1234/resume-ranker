import React from "react";

function ResultCard({ result }) {
  return (
    <div className="card">
      <div className="header">
        <h3>{result.name || "Candidate"}</h3>
        <div className="score">Overall: {result.overall_score}</div>
      </div>
      <div className="row">
        <b>Skill match:</b> {result.skill_match_score}
      </div>
      <div className="row">
        <b>Experience:</b> {result.experience_score}
      </div>
      <div className="row">
        <b>Matched Skills:</b> {result.matched_skills && result.matched_skills.join(", ")}
      </div>
      <div className="row">
        <b>Top Experiences:</b>
        <ul>
          {result.demonstrated_experiences && result.demonstrated_experiences.map((b, i) => (
            <li key={i}>{b.text}</li>
          ))}
        </ul>
      </div>
      <div className="row explain">
        <b>Explain:</b> {result.explainability}
      </div>
    </div>
  );
}

export default ResultCard;
