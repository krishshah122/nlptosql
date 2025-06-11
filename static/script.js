let currentQuery = ""

// Show status messages
function showStatus(message, type = "info") {
  const statusEl = document.getElementById("statusMessage")
  statusEl.textContent = message
  statusEl.className = `status-message ${type} show`

  setTimeout(() => {
    statusEl.classList.remove("show")
  }, 3000)
}

// Generate SQL query from natural language
async function generateQuery() {
  const question = document.getElementById("questionInput").value.trim()

  if (!question) {
    showStatus("Please enter a question!", "error")
    return
  }

  const generateBtn = document.getElementById("generateBtn")
  const originalText = generateBtn.textContent
  generateBtn.innerHTML = '<span class="spinner"></span> Generating...'
  generateBtn.disabled = true

  try {
    const response = await fetch("/generate-query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question }),
    })

    const data = await response.json()

    if (data.success) {
      currentQuery = data.query
      document.getElementById("generatedQuery").textContent = data.query
      document.getElementById("querySection").style.display = "block"
      showStatus("Query generated successfully!", "success")
    } else {
      showStatus("Failed to generate query", "error")
    }
  } catch (error) {
    showStatus("Error generating query: " + error.message, "error")
  } finally {
    generateBtn.textContent = originalText
    generateBtn.disabled = false
  }
}

// Copy query to clipboard
async function copyQuery() {
  if (!currentQuery) return

  try {
    await navigator.clipboard.writeText(currentQuery)
    showStatus("Query copied to clipboard!", "success")
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement("textarea")
    textArea.value = currentQuery
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand("copy")
    document.body.removeChild(textArea)
    showStatus("Query copied to clipboard!", "success")
  }
}

// Execute SQL query
async function executeQuery() {
  if (!currentQuery) {
    showStatus("No query to execute!", "error")
    return
  }

  try {
    const response = await fetch("/execute-query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sql: currentQuery }),
    })

    const data = await response.json()

    if (data.success) {
      displayResults(data)
      showStatus(`Query executed successfully! ${data.row_count || data.affected_rows || 0} rows affected.`, "success")
    } else {
      showStatus("Query execution failed", "error")
    }
  } catch (error) {
    showStatus("Error executing query: " + error.message, "error")
  }
}

// Display query results
function displayResults(data) {
  const resultsContainer = document.getElementById("resultsContainer")
  const resultsSection = document.getElementById("resultsSection")

  if (data.data && data.data.length > 0) {
    // Create table
    let html = `
            <div class="results-info">
                <p><strong>Rows returned:</strong> ${data.row_count}</p>
            </div>
            <table class="results-table">
                <thead>
                    <tr>
        `

    // Add headers
    data.columns.forEach((col) => {
      html += `<th>${col}</th>`
    })
    html += "</tr></thead><tbody>"

    // Add data rows
    data.data.forEach((row) => {
      html += "<tr>"
      data.columns.forEach((col) => {
        html += `<td>${row[col] || ""}</td>`
      })
      html += "</tr>"
    })

    html += "</tbody></table>"
    resultsContainer.innerHTML = html
  } else if (data.message) {
    resultsContainer.innerHTML = `<p class="success-message">${data.message}</p>`
  } else {
    resultsContainer.innerHTML = "<p>No results returned.</p>"
  }

  resultsSection.style.display = "block"
}

// Explain query
async function explainQuery() {
  if (!currentQuery) {
    showStatus("No query to explain!", "error")
    return
  }

  try {
    const response = await fetch("/explain-query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sql: currentQuery }),
    })

    const data = await response.json()

    if (data.explanation) {
      alert(`Query Explanation:\n\n${data.explanation}`)
    }
  } catch (error) {
    showStatus("Error explaining query: " + error.message, "error")
  }
}

// Upload CSV data
async function uploadData() {
  const fileInput = document.getElementById("csvFile")
  const file = fileInput.files[0]

  if (!file) {
    showStatus("Please select a CSV file!", "error")
    return
  }

  const formData = new FormData()
  formData.append("file", file)

  try {
    showStatus("Uploading data...", "info")

    const response = await fetch("/upload-data", {
      method: "POST",
      body: formData,
    })

    const data = await response.json()

    if (data.success) {
      showStatus(`Data uploaded successfully! ${data.rows} rows added to table.`, "success")
      fileInput.value = "" // Clear file input
      showSchema() // Refresh schema
    } else {
      showStatus("Upload failed", "error")
    }
  } catch (error) {
    showStatus("Error uploading data: " + error.message, "error")
  }
}

// Show database schema
async function showSchema() {
  try {
    const response = await fetch("/schema")
    const data = await response.json()

    const schemaContainer = document.getElementById("schemaContainer")

    if (Object.keys(data.schema).length === 0) {
      schemaContainer.innerHTML = "<p>No tables found. Upload some data first!</p>"
      return
    }

    let html = ""
    for (const [tableName, columns] of Object.entries(data.schema)) {
      html += `
                <div class="schema-table">
                    <h4>📊 ${tableName}</h4>
                    <ul>
            `

      columns.forEach((col) => {
        html += `<li><strong>${col.name}</strong> - ${col.type}</li>`
      })

      html += "</ul></div>"
    }

    schemaContainer.innerHTML = html
  } catch (error) {
    showStatus("Error loading schema: " + error.message, "error")
  }
}

// Handle Enter key in textarea
document.getElementById("questionInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) {
    generateQuery()
  }
})

// Load schema on page load
document.addEventListener("DOMContentLoaded", () => {
  showSchema()
})

// Add some example questions
const examples = [
  "Show me all data",
  "Count total records",
  "Sabse zyada salary wala employee",
  "Top 5 customers by revenue",
  "Average age of users",
  "Kitne unique cities hain",
]

// Add example buttons
function addExamples() {
  const questionInput = document.getElementById("questionInput")
  const exampleButtons = document.createElement("div")
  exampleButtons.className = "example-buttons"
  exampleButtons.innerHTML = "<p><strong>Quick Examples:</strong></p>"

  examples.forEach((example) => {
    const btn = document.createElement("button")
    btn.textContent = example
    btn.className = "example-btn"
    btn.onclick = () => {
      questionInput.value = example
    }
    exampleButtons.appendChild(btn)
  })

  questionInput.parentNode.insertBefore(exampleButtons, questionInput.nextSibling)
}
document.getElementById('generateChartForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const response = await fetch('/generate-chart', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  if (data.success) {
    document.getElementById('chartFrame').src = data.chart_url;
    document.getElementById('chartSection').style.display = 'block';
  } else {
    alert('Chart generation failed.');
  }
});


document.getElementById('viewDashboardForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const user_id = formData.get('user_id');

  const response = await fetch(`/dashboard/${user_id}`);
  const data = await response.json();

  if (data.success) {
    document.getElementById('dashboardContainer').innerText = JSON.stringify(data.charts, null, 2);
  } else {
    alert('Dashboard loading failed.');
  }
});
// ✅ added missing closing bracket for this event listener


// Add CSS for example buttons
const style = document.createElement("style")
style.textContent = `
    .example-buttons {
        margin-top: 15px;
    }
    .example-buttons p {
        margin-bottom: 10px;
        color: #666;
    }
    .example-btn {
        background: #e2e8f0;
        color: #4a5568;
        border: 1px solid #cbd5e0;
        padding: 8px 12px;
        margin: 5px;
        border-radius: 20px;
        font-size: 14px;
        cursor: pointer;
    }
    .example-btn:hover {
        background: #cbd5e0;
        transform: none;
        box-shadow: none;
    }
`
document.head.appendChild(style)

// Initialize examples
document.addEventListener("DOMContentLoaded", addExamples)
