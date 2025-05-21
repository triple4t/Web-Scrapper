"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader } from "lucide-react";

export default function ScrapedContent() {
  const router = useRouter();
  const [content, setContent] = useState(""); 
  const [summary, setSummary] = useState(""); 
  const [loading, setLoading] = useState(false); 

  useEffect(() => {
    const scrapedContent = localStorage.getItem("scrapedContent");
    if (scrapedContent) {
      setContent(scrapedContent);
    }
  }, []);

  const handleSummarize = async () => {
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/summarize-text/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: content }),
      });

      if (!response.ok) throw new Error("Failed to summarize content");

      const data = await response.json();
      setSummary(data.summary); 
      setLoading(false); 
    } catch (error) {
      alert("Error summarizing content. Please try again.");
      setLoading(false); 
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-4xl mx-auto py-12 px-6">
        <h1 className="text-3xl font-bold text-center mb-6">Scraped Content</h1>

        <div className="bg-gray-100 p-6 rounded-lg shadow-md">
          <pre className="whitespace-pre-wrap text-lg leading-relaxed">
            {content}
          </pre>
        </div>

        {content && (
          <div className="flex justify-center mt-6">
            <button
              onClick={handleSummarize} 
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition duration-300"
            >
              {loading ? (
                <Loader className="animate-spin w-5 h-5 mr-2" />
              ) : null}
              {loading ? "Summarizing..." : "Summarize"}
            </button>
          </div>
        )}

        {summary && (
          <div className="mt-6 bg-gray-100 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Summary:</h2>
            <p>{summary}</p>
          </div>
        )}

        <div className="flex justify-center mt-6">
          <button
            onClick={() => router.push("/")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition duration-300"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
