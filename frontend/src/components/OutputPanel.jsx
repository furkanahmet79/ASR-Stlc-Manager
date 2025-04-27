import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useSelector } from 'react-redux';

export default function OutputPanel({ output, activeTab, processes }) {
  const { status: codeReviewStatus, reviews, error: codeReviewError } = useSelector(state => state.codeReview || {});
  const { status: reqStatus, result: reqResult, error: reqError } = useSelector(state => state.requirementAnalysis || {});
  const { status: testPlanningStatus, plans, error: testPlanningError } = useSelector(state => state.testPlanning || {});
  const { status: envSetupStatus, setups, error: envSetupError } = useSelector(state => state.environmentSetup || {});

  const processId = activeTab !== 'pipeline' && activeTab !== 'files' ? activeTab : null;
  const selectedProcess = processes?.find(p => p.id === processId);
  const processOutput = processId && output && output.processId === processId ? output : null;
  const processName = selectedProcess?.name || '';
  const headerTitle = processId ? `${processName} Output` : 'Output';

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
      if (plans && plans.length > 0 && typeof plans[0] === 'object' && plans[0] !== null && 'files' in plans[0] && 'plan' in plans[0]) {
        const filesMarkdown = plans[0].files;
        const planData = plans[0].plan;

        return (
          <div className="space-y-4">
            <div className="prose prose-sm max-w-none text-gray-600">
              <ReactMarkdown>{filesMarkdown}</ReactMarkdown>
            </div>
            <div className="bg-gray-100 rounded p-4 font-mono text-xs overflow-auto">
              <pre className="whitespace-pre-wrap break-words">
                {JSON.stringify(planData, null, 2)}
              </pre>
            </div>
          </div>
        );
      } else if (plans && plans.length > 0) {
        console.warn("Beklenmeyen plans[0] yapısı (JSON gösterimi bekleniyor):", plans[0]);
        return (
          <div className="bg-gray-100 rounded p-4 font-mono text-xs overflow-auto">
            <pre className="whitespace-pre-wrap break-words">
              {JSON.stringify(plans[0], null, 2)}
            </pre>
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
        // JSON içeriğini ayıkla
        const setupContent = setups.map(setup => setup).join('\n\n');
        // JSON stringini tespit et
        const jsonMatch = setupContent.match(/\{[\s\S]*\}/);
        let prettyJson = null;
        if (jsonMatch) {
          try {
            prettyJson = JSON.stringify(JSON.parse(jsonMatch[0]), null, 2);
          } catch (e) {
            prettyJson = jsonMatch[0];
          }
        }
        currentOutput = {
          content: setupContent,
          prettyJson,
          status: 'completed',
          timestamp: new Date().toISOString(),
          processType: 'Environment Setup'
        };
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