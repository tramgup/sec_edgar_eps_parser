import { useState } from "react";

export default function App() {
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleFileChange(event) {
    setFiles(event.target.files);
  }

  async function handleSubmit() {
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
      formData.append("file", file);
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult({ ok: false, error: "Something went wrong" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>File Upload UI</h1>
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleSubmit} disabled={loading} style={{ marginLeft: "1rem" }}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {result && result.ok && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Results</h2>
          <table style={{ 
            width: "100%", 
            borderCollapse: "collapse",
            marginTop: "1rem",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <thead>
              <tr style={{ backgroundColor: "#4F46E5", color: "white" }}>
                <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #ddd" }}>
                  Filename
                </th>
                <th style={{ padding: "12px", textAlign: "right", borderBottom: "2px solid #ddd" }}>
                  EPS
                </th>
              </tr>
            </thead>
            <tbody>
              {result.result.map((item, index) => (
                <tr 
                  key={index}
                  style={{ 
                    backgroundColor: index % 2 === 0 ? "#F9FAFB" : "white",
                    transition: "background-color 0.2s"
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#E0E7FF"}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = index % 2 === 0 ? "#F9FAFB" : "white"}
                >
                  <td style={{ padding: "12px", borderBottom: "1px solid #E5E7EB" }}>
                    {item.filename}
                  </td>
                  <td style={{ 
                    padding: "12px", 
                    textAlign: "right", 
                    borderBottom: "1px solid #E5E7EB",
                    color: item.eps >= 0 ? "#059669" : "#DC2626",
                    fontWeight: "600"
                  }}>
                    {item.eps.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {result && !result.ok && (
        <div style={{ 
          marginTop: "2rem", 
          padding: "1rem", 
          backgroundColor: "#FEE2E2", 
          border: "1px solid #DC2626",
          borderRadius: "4px",
          color: "#991B1B"
        }}>
          <strong>Error:</strong> {result.error}
        </div>
      )}
      </div>
  );
}
