import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useSelector } from 'react-redux';
import { Gantt, ViewMode } from 'gantt-task-react';
import "gantt-task-react/dist/index.css";

// JSON'dan XML'e dönüştürme fonksiyonu
function jsonToXml(jsonData) {
  try {
    // JSON string ise parse et
    const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
    
    // Eğer bir dizi ise
    if (Array.isArray(data)) {
      let xml = '<TestPlan>\n';
      
      data.forEach(task => {
        xml += '  <Task>\n';
        for (const key in task) {
          // Key adını XML tag formatına çevir (boşlukları kaldır)
          const tagName = key.replace(/\s+/g, '');
          xml += `    <${tagName}>${task[key]}</${tagName}>\n`;
        }
        xml += '  </Task>\n';
      });
      
      xml += '</TestPlan>';
      return xml;
    } else {
      // Tek bir obje ise
      let xml = '<TestPlan>\n  <Task>\n';
      
      for (const key in data) {
        const tagName = key.replace(/\s+/g, '');
        xml += `    <${tagName}>${data[key]}</${tagName}>\n`;
      }
      
      xml += '  </Task>\n</TestPlan>';
      return xml;
    }
  } catch (error) {
    console.error('JSON to XML conversion error:', error);
    return `<!-- Error converting JSON to XML: ${error.message} -->`;
  }
}

// JSON formatını Gantt Chart için task listesine dönüştürme
function jsonToGanttTasks(jsonData) {
  try {
    // JSON string ise parse et
    const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
    
    if (!Array.isArray(data)) {
      console.error('Gantt data is not an array');
      return [];
    }
    
    // Gantt Chart için task listesi oluştur
    return data.map((task, index) => {
      // Tarihleri parse et
      const startDate = parseDate(task["Start Date"]);
      const endDate = parseDate(task["End Date"]);
      
      return {
        id: `task-${index}`,
        name: task["Task Name"],
        start: startDate,
        end: endDate,
        progress: 0, // Varsayılan ilerleme
        type: 'task',
        isDisabled: false,
        styles: { progressColor: '#0275d8', progressSelectedColor: '#0275d8' }
      };
    });
  } catch (error) {
    console.error('JSON to Gantt conversion error:', error);
    return [];
  }
}

// Tarih formatlarını işleme
function parseDate(dateStr) {
  if (!dateStr) return new Date();
  
  // YYYY-MM-DD formatını kontrol et
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    return new Date(dateStr);
  }
  
  // Bugün+N formatını işle (ör: "today+5")
  if (dateStr.toLowerCase().includes('today+')) {
    const daysToAdd = parseInt(dateStr.split('+')[1], 10) || 0;
    const result = new Date();
    result.setDate(result.getDate() + daysToAdd);
    return result;
  }
  
  // Diğer durumlar için geçerli bir tarih döndür
  return new Date(dateStr);
}

// Görevlerin toplam süresine göre uygun görünümü ve sütun genişliğini seçen fonksiyon
function getGanttViewModeAndColumnWidth(tasks) {
  if (!tasks || tasks.length === 0) {
    return { viewMode: ViewMode.Week, columnWidth: 50 };
  }
  // En erken başlangıç ve en geç bitiş tarihini bul
  const minDate = new Date(Math.min(...tasks.map(t => t.start)));
  const maxDate = new Date(Math.max(...tasks.map(t => t.end)));
  const diffDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24));

  if (diffDays > 365) {
    return { viewMode: ViewMode.Year, columnWidth: 60 };
  } else if (diffDays > 90) {
    return { viewMode: ViewMode.Month, columnWidth: 60 };
  } else if (diffDays > 30) {
    return { viewMode: ViewMode.Week, columnWidth: 50 };
  } else {
    return { viewMode: ViewMode.Day, columnWidth: 40 };
  }
}

export default function OutputPanel({ output, activeTab, processes, outputFormats }) {
  const { status: codeReviewStatus, reviews, error: codeReviewError } = useSelector(state => state.codeReview || {});
  const { status: reqStatus, result: reqResult, error: reqError } = useSelector(state => state.requirementAnalysis || {});
  const { status: testPlanningStatus, plans, error: testPlanningError } = useSelector(state => state.testPlanning || {});
  const { status: envSetupStatus, setups, error: envSetupError } = useSelector(state => state.environmentSetup || {});

  const processId = activeTab !== 'pipeline' && activeTab !== 'files' ? activeTab : null;
  const selectedProcess = processes?.find(p => p.id === processId);
  const processOutput = processId && output && output.processId === processId ? output : null;
  const processName = selectedProcess?.name || '';
  const headerTitle = processId ? `${processName} Output` : 'Output';
  
  // Seçilen output formatını al
  const selectedOutputFormat = outputFormats?.[processId];

  const getSampleOutput = () => {
    if (!processId) return null;
    const samples = {
      'code-review': {
        content: "## Code Review Results\n\n### main.js\n- Function `calculateTotal()` lacks input validation\n- Consider adding error handling for edge cases\n\n### utils.js\n- Good use of modular design\n- Line 42: Potential memory leak in event listener",
        status: 'sample',
        timestamp: new Date().toISOString()
      },
      'test-planning': {
        content: "## Test Planning Document\n\n### Test Objectives\n1. Validate user authentication flows\n2. Verify data integrity across transactions\n\n### Test Scenarios\n- Login with valid credentials\n- Login with invalid credentials\n- Password reset flow",
        status: 'sample',
        timestamp: new Date().toISOString()
      },
      'requirement-analysis': {
        content: "## Requirements Analysis\n\n### Functional Requirements\n- User registration system\n- Product catalog browsing\n- Shopping cart functionality\n\n### Non-Functional Requirements\n- System should support 1000 concurrent users\n- Page load time < 2 seconds",
        status: 'sample',
        timestamp: new Date().toISOString()
      },
      'environment-setup': {
        content: "## Environment Setup Guide\n\n### Development Environment\n```\nnpm install\nnpm run setup-dev\n```\n\n### Testing Environment\n```\ndocker-compose up -d\nnpm run setup-test\n```",
        status: 'sample',
        timestamp: new Date().toISOString()
      },
      'test-scenario-generation': {
        content: "## Generated Test Scenarios\n\n### User Authentication\n1. **TC001**: Verify login with valid username and password\n2. **TC002**: Verify login with invalid credentials\n3. **TC003**: Verify password reset functionality\n\n### Shopping Cart\n1. **TC004**: Add single item to cart\n2. **TC005**: Add multiple items to cart",
        status: 'sample',
        timestamp: new Date().toISOString()
      }
    };
    return samples[processId] || {
      content: `# ${processName} Output\n\nRun this process to see actual output here.`,
      status: 'sample',
      timestamp: new Date().toISOString()
    };
  };

  const displayOutput = processOutput || (processId && !output ? getSampleOutput() : output);

  const renderCodeReviewOutput = () => {
    if (codeReviewStatus === 'loading') {
      return <div>Loading code review results...</div>;
    }
    
    if (codeReviewError) {
      return <div className="text-red-600">Error: {codeReviewError}</div>;
    }
    
    if (reviews.length === 0) {
      return <div>No code review results available</div>;
    }
    
    return (
      <div className="prose prose-sm max-w-none">
        {reviews.map((review, index) => (
          <div key={index} className="mb-4">
            <ReactMarkdown>{review}</ReactMarkdown>
          </div>
        ))}
      </div>
    );
  };

  const renderContent = () => {
    let currentOutput = { ...getSampleOutput() };

    if (activeTab === 'code-review') {
      if (codeReviewStatus === 'loading') {
        return <div>Loading code review results...</div>;
      }
      if (codeReviewError) {
        return <div className="text-red-600">Error: {codeReviewError}</div>;
      }
      if (reviews && reviews.length > 0) {
        const reviewContent = reviews.map(review => review).join('\n\n');
        currentOutput = {
          content: reviewContent,
          status: 'completed',
          timestamp: new Date().toISOString(),
          processType: 'Code Review'
        };
      }
    }

    if (activeTab === 'requirement-analysis') {
      if (reqStatus === 'loading') {
        return <div>Loading requirement analysis results...</div>;
      }
      if (reqError) {
        return <div className="text-red-600">Error: {reqError}</div>;
      }
      if (reqResult && Array.isArray(reqResult.analysis) && reqResult.analysis.length > 0) {
        const analysisContent = reqResult.analysis.map(item => `## Files Analyzed\n${item.files}\n\n## Analysis\n${item.result}`).join('\n\n');
        return (
          <div className="space-y-4">
            <section>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium">Process Results</h3>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
                <div className="prose prose-sm max-w-none text-gray-600">
                  <ReactMarkdown>{analysisContent}</ReactMarkdown>
                </div>
              </div>
            </section>
            <section>
              <h3 className="text-lg font-medium mb-3">Execution Details</h3>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
                <div className="text-gray-600">
                  <p><strong>Status:</strong> completed</p>
                  <p><strong>Process:</strong> Requirement Analysis</p>
                  <p><strong>Last Updated:</strong> {new Date().toLocaleString()}</p>
                </div>
              </div>
            </section>
          </div>
        );
      }
      // Sample göster
      return (
        <div className="space-y-4">
          <section>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium">Process Results</h3>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                Sample
              </span>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="prose prose-sm max-w-none text-gray-600">
                <ReactMarkdown>{getSampleOutput().content}</ReactMarkdown>
              </div>
            </div>
          </section>
          <section>
            <h3 className="text-lg font-medium mb-3">Execution Details</h3>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="text-gray-600">
                <p><strong>Status:</strong> Not Run</p>
                <p><strong>Process:</strong> Requirement Analysis</p>
                <p><strong>Last Updated:</strong> {new Date().toLocaleString()}</p>
              </div>
            </div>
          </section>
        </div>
      );
    }

    if (activeTab === 'test-planning') {
      if (testPlanningStatus === 'loading') {
        return <div>Loading test planning results...</div>;
      }
      if (testPlanningError) {
        return <div className="text-red-600">Error: {testPlanningError}</div>;
      }
      if (plans && plans.length > 0) {
        // Text olarak gelen JSON planını çıkar
        let planContent = plans[0];
        const jsonMatch = planContent.match(/```json\n([\s\S]*?)```/);
        let jsonContent = null;
        let filesSection = "";
        let ganttTasks = [];
        let ganttParseError = false;
        
        // JSON kısmını ve files section kısmını ayır
        if (jsonMatch) {
          jsonContent = jsonMatch[1];
          // Files kısmını ayıkla
          const filesSectionMatch = planContent.match(/## Files Analyzed\n([\s\S]*?)\n\n## Test Plan/);
          if (filesSectionMatch) {
            filesSection = filesSectionMatch[1];
          }
          // Gantt Chart için task listesi oluştur
          try {
            ganttTasks = jsonToGanttTasks(jsonContent);
          } catch (e) {
            console.error('Error creating Gantt tasks:', e);
            ganttParseError = true;
          }
        }
        // Eğer JSON ayrıştırılamadıysa veya Gantt parse hatası varsa, sadece model çıktısını göster
        if (!jsonContent || ganttParseError) {
          return (
            <div className="mt-6">
              <div className="bg-yellow-100 text-yellow-800 p-4 rounded">
                <strong>Model çıktısı (JSON ayrıştırılamadı veya hatalı):</strong>
                <pre className="mt-2 whitespace-pre-wrap break-words text-xs bg-gray-50 p-2 rounded">{planContent}</pre>
              </div>
            </div>
          );
        }
        
        return (
          <div className="space-y-6">
            <div className="prose prose-sm max-w-none text-gray-600">
              <h2>Files Analyzed</h2>
              <ReactMarkdown>{filesSection}</ReactMarkdown>
            </div>
            
            {/* JSON veya XML formatında göster */}
            <div className="bg-gray-100 rounded p-4 font-mono text-xs overflow-auto">
              <h2 className="text-lg font-medium mb-2">Test Plan {selectedOutputFormat === 'XML' ? '(XML Format)' : '(JSON Format)'}</h2>
              <pre className="whitespace-pre-wrap break-words">
                {selectedOutputFormat === 'XML' && jsonContent 
                  ? jsonToXml(jsonContent)
                  : jsonContent}
              </pre>
            </div>
            
            {/* Gantt Chart Görünümü */}
            {ganttTasks.length > 0 ? (
              <div className="mt-6">
                <h2 className="text-lg font-medium mb-2">Test Plan Gantt Chart</h2>
                <div className="border rounded-lg p-4 bg-white overflow-x-auto">
                  <div style={{ width: '100%', minWidth: '800px', height: '400px' }}>
                    {/* Dinamik görünüm ve sütun genişliği, hata olursa model çıktısı göster */}
                    {(() => {
                      try {
                        const { viewMode, columnWidth } = getGanttViewModeAndColumnWidth(ganttTasks);
                        return (
                          <Gantt
                            tasks={ganttTasks}
                            viewMode={viewMode}
                            listCellWidth="150px"
                            columnWidth={columnWidth}
                            headerHeight={50}
                            rowHeight={40}
                            ganttHeight={400}
                          />
                        );
                      } catch (err) {
                        console.error('Gantt Chart render error:', err);
                        return (
                          <div className="bg-red-100 text-red-700 p-4 rounded">
                            <strong>Gantt Chart oluşturulamadı. Model çıktısı:</strong>
                            <pre className="mt-2 whitespace-pre-wrap break-words text-xs bg-gray-50 p-2 rounded">{jsonContent}</pre>
                          </div>
                        );
                      }
                    })()}
                  </div>
                </div>
              </div>
            ) : (
              jsonContent && (
                <div className="mt-6">
                  <div className="bg-yellow-100 text-yellow-800 p-4 rounded">
                    <strong>Gantt Chart oluşturulamadı veya görev bulunamadı. Model çıktısı:</strong>
                    <pre className="mt-2 whitespace-pre-wrap break-words text-xs bg-gray-50 p-2 rounded">{jsonContent}</pre>
                  </div>
                </div>
              )
            )}
          </div>
        );
      }
      // Sample göster
      return (
        <div className="space-y-4">
          <section>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium">Process Results</h3>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                Sample
              </span>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="prose prose-sm max-w-none text-gray-600">
                <ReactMarkdown>{getSampleOutput().content}</ReactMarkdown>
              </div>
            </div>
          </section>
          <section>
            <h3 className="text-lg font-medium mb-3">Execution Details</h3>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="text-gray-600">
                <p><strong>Status:</strong> Not Run</p>
                <p><strong>Process:</strong> Test Planning</p>
                <p><strong>Last Updated:</strong> {new Date().toLocaleString()}</p>
              </div>
            </div>
          </section>
        </div>
      );
    }

    if (activeTab === 'environment-setup') {
      if (envSetupStatus === 'loading') {
        return <div> Loading Environment setup results...</div>;
      }
      if (envSetupError) {
        return <div className="text-red-600">Hata: {envSetupError}</div>;
      }
      if (setups && setups.length > 0) {
        // Text olarak gelen JSON planını çıkar
        let setupContent = setups[0];
        const jsonMatch = setupContent.match(/\{[\s\S]*\}/);
        let jsonContent = null;
        let filesSection = "";
        
        // Files kısmını ayıkla
        const filesSectionMatch = setupContent.match(/## Files Analyzed\n([\s\S]*?)\n\n## Environment Setup/);
        if (filesSectionMatch) {
          filesSection = filesSectionMatch[1];
        }
        
        // JSON içeriğini bul
        if (jsonMatch) {
          jsonContent = jsonMatch[0];
          try {
            // JSON formatını düzgünce formatla
            const jsonObject = JSON.parse(jsonContent);
            jsonContent = JSON.stringify(jsonObject, null, 2);
          } catch (e) {
            console.error('JSON parse error:', e);
          }
        }
        
        return (
          <div className="space-y-4">
            <div className="prose prose-sm max-w-none text-gray-600">
              <h2>Files Analyzed</h2>
              <ReactMarkdown>{filesSection}</ReactMarkdown>
            </div>
            
            {/* JSON veya XML formatında göster */}
            <div className="bg-gray-100 rounded p-4 font-mono text-xs overflow-auto">
              <h2 className="text-lg font-medium mb-2">Environment Setup {selectedOutputFormat === 'XML' ? '(XML Format)' : '(JSON Format)'}</h2>
              <pre className="whitespace-pre-wrap break-words">
                {selectedOutputFormat === 'XML' && jsonContent 
                  ? jsonToXml(jsonContent)
                  : jsonContent}
              </pre>
            </div>
          </div>
        );
      }
    }

    if (!currentOutput) {
      return (
        <div className="h-full flex items-center justify-center">
          <div className="text-center space-y-3">
            {/* ...existing empty state JSX... */}
          </div>
        </div>
      );
    }

    // Ensure content is a string
    const content = typeof currentOutput.content === 'string' 
      ? currentOutput.content 
      : JSON.stringify(currentOutput.content || 'No content available');

    return (
      <div className="space-y-4">
        <section>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-medium">Process Results</h3>
            {currentOutput.status === 'sample' && (
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                Sample
              </span>
            )}
          </div>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
            <div className="prose prose-sm max-w-none text-gray-600">
              {/* Önce açıklama kısmı, sonra kod bloğu */}
              <ReactMarkdown>{content.replace(/\{[\s\S]*\}/, '').trim()}</ReactMarkdown>
              {currentOutput.prettyJson && (
                <div className="bg-gray-100 rounded p-4 font-mono text-xs overflow-auto mt-4">
                  <pre className="whitespace-pre-wrap break-words">{currentOutput.prettyJson}</pre>
                </div>
              )}
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-lg font-medium mb-3">Execution Details</h3>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
            <div className="text-gray-600">
              <p><strong>Status:</strong> {currentOutput.status === 'sample' ? 'Not Run' : currentOutput.status}</p>
              <p><strong>Process:</strong> {processName || currentOutput.processType || 'Unknown'}</p>
              <p><strong>Last Updated:</strong> {new Date(currentOutput.timestamp).toLocaleString()}</p>
            </div>
          </div>
        </section>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-none h-16 px-6 flex items-center justify-between border-b border-gray-200 bg-white">
        <h2 className="text-xl font-bold text-gray-900">{headerTitle}</h2>
        {processId && (
          <span className="px-3 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-800">
            {processId}
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {renderContent()}
      </div>
      <div className="flex-none h-16 px-6 flex items-center border-t border-gray-200 bg-white">
        <button
          className={`w-full py-2 px-4 rounded-md text-white transition-colors shadow-sm ${
            !displayOutput || displayOutput.status === 'sample'
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700'
          }`}
          disabled={!displayOutput || displayOutput.status === 'sample'}
        >
          Install Output
        </button>
      </div>
    </div>
  );
}