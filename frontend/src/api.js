/**
 * Centralized API layer for Resume Ranker
 * All frontend → backend calls live here
 */

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Health check (optional)
 */
export async function healthCheck() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error("Backend health check failed");
  }
  return res.json();
}

/**
 * Rank resumes against a Job Description
 *
 * @param {File} zipFile - ZIP containing resumes (PDF/images)
 * @param {string} jobDescription - JD text
 * @param {number} topK - number of results to return
 * @param {number} skillVsExpWeight - 0..1 weighting
 *
 * @returns {Promise<Object>} ranking JSON
 */
export async function rankResumes({
  zipFile,
  jobDescription,
  topK = 10,
  skillVsExpWeight = 0.5,
}) {
  if (!zipFile) {
    throw new Error("ZIP file is required");
  }
  if (!jobDescription || jobDescription.trim().length === 0) {
    throw new Error("Job description is required");
  }

  const formData = new FormData();
  formData.append("resumes_zip", zipFile);
  formData.append("job_description", jobDescription);
  formData.append("top_k", topK);
  formData.append("skill_vs_exp_weight", skillVsExpWeight);

  const response = await fetch(`${API_BASE_URL}/rank`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Ranking failed: ${text}`);
  }

  return response.json();
}
