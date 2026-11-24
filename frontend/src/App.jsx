// AI Document Intelligence Platform — React starter placeholder.
// Portfolio documentation and starter skeleton based on the resume
// description; not the original production code.
// The fetch calls below are stubs only.

import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [message, setMessage] = useState("");

  async function handleUpload(event) {
    event.preventDefault();
    // TODO: POST /documents/upload with the selected file.
    setMessage("Upload is a starter stub — TODO: wire up POST /documents/upload.");
  }

  async function handleAsk(event) {
    event.preventDefault();
    // TODO: POST /query with the question and show the source-grounded answer.
    setAnswer("");
    setMessage("Ask is a starter stub — TODO: wire up POST /query.");
  }

  return (
    <main>
      <h1>AI Document Intelligence Platform</h1>
      <p>Upload documents and ask source-grounded questions.</p>

      <section>
        <h2>Upload a document</h2>
        <form onSubmit={handleUpload}>
          <input
            type="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button type="submit" disabled={!file}>
            Upload
          </button>
        </form>
      </section>

      <section>
        <h2>Ask a question</h2>
        <form onSubmit={handleAsk}>
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about your documents"
          />
          <button type="submit" disabled={!question}>
            Ask
          </button>
        </form>
        {answer && <p>{answer}</p>}
      </section>

      {message && <p>{message}</p>}
    </main>
  );
}
