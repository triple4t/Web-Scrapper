"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader } from "lucide-react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/scrape/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error("Failed to scrape");

      const data = await response.json();
      setLoading(false);

      localStorage.setItem("scrapedContent", data.content);
      localStorage.setItem("scrapedUrl", url);

      router.push("/scraped-content");
    } catch (error) {
      alert("Error fetching data. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4">
      <div className="bg-white shadow-lg rounded-lg p-6 md:p-8 w-full max-w-lg">
        <h1 className="text-2xl font-semibold text-gray-800 text-center mb-4">
          Web Scraper
        </h1>
        <p className="text-gray-500 text-center mb-6">
          Enter a website URL to extract its text content.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="url"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition duration-300 flex items-center justify-center"
          >
            {loading ? <Loader className="animate-spin w-5 h-5 mr-2" /> : null}
            {loading ? "Scraping..." : "Scrape Website"}
          </button>
        </form>
      </div>
    </div>
  );
}
