// AI Document Intelligence Platform — real React UI.
// Upload .pdf / .txt / .md, list documents, ask a question and see
// the source-grounded answer with its sources.
//
// API base: VITE_API_URL when set (Docker), otherwise the Vite dev
// proxy / same origin in dev, falling back to localhost:8000.
import { useCallback, useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/documents`);
      if (!res.ok) throw new Error("Backend is unavailable — start it with docker compose up.");
      setDocuments(await res.json());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed.");
      setMessage(data.message);
      setFile(null);
      event.target.reset();
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleAsk(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setAnswer(null);
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 5 }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed.");
      setAnswer(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id) {
    try {
      const res = await fetch(`${API_URL}/documents/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed.");
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main>
      <h1>AI Document Intelligence Platform</h1>
      <p>Upload documents and ask source-grounded questions. Answers are built only from your uploaded documents — no API key is required.</p>

      {error && <p className="error">{error}</p>}
      {message && <p>{message}</p>}

      <section>
        <h2>Upload a document</h2>
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <button type="submit" disabled={!file || busy}>
            {busy ? "Uploading…" : "Upload"}
          </button>
        </form>
        <p className="meta">Accepted: .pdf, .txt, .md</p>
      </section>

      <section>
        <h2>Documents ({documents.length})</h2>
        {documents.length === 0 ? (
          <p className="meta">No documents yet — upload one above.</p>
        ) : (
          <ul>
            {documents.map((doc) => (
              <li key={doc.id}>
                {doc.filename} — {doc.chunk_count} chunks
                {" "}
                <button type="button" onClick={() => handleDelete(doc.id)}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>Ask a question</h2>
        <form onSubmit={handleAsk}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about your documents"
          />
          <button type="submit" disabled={!question.trim() || busy}>
            {busy ? "Searching…" : "Ask"}
          </button>
        </form>
        {answer && (
          <div>
            <p>{answer.answer}</p>
            <p className="meta">
              Answer type: {answer.answer_type}
              {answer.cached ? " (cached)" : ""}
            </p>
            <h3>Sources</h3>
            {answer.sources.length === 0 ? (
              <p className="meta">No sources found.</p>
            ) : (
              answer.sources.map((src, i) => (
                <div className="source" key={i}>
                  <strong>{src.document_name}</strong> (chunk {src.chunk_index}, score {src.score})
                  <p>{src.text}</p>
                </div>
              ))
            )}
          </div>
        )}
      </section>
    </main>
  );
}
