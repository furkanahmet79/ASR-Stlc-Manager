import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/processes';

export const processService = {
  async runProcess(processType, files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      console.log(`İstek gönderiliyor: ${processType} süreci için`);
      const response = await axios.post(
        `${API_BASE_URL}/processes/${processType}/run`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      console.log(`İstek başarıyla gönderildi: ${processType} süreci`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || `Failed to run ${processType}`);
    }
  },

  async runCodeReview(files, model = null, customPrompt = null, sessionId = null) {
    console.log('[ProcessService] Running code review with model:', model);
    
    const formData = new FormData();
    files.forEach(fileInfo => {
      const file = fileInfo.file || fileInfo;
      formData.append('files', file);
    });
    
    if (model) {
      formData.append('model', model);
    }
    if (customPrompt) {
      console.log('processService.js - custom_prompt gönderiliyor:', customPrompt);
      formData.append('custom_prompt', customPrompt);
    }
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/code-review/run`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      // Redux action payload formatına uygun dönüş
      return {
        reviews: data.reviews.map(review => `## Files Analyzed\n${review.files}\n\n## Review\n${review.review}`),
        metadata: {
          timestamp: new Date().toISOString(),
          fileCount: files.length
        }
      };
    } catch (error) {
      throw error;
    }
  },

  // Yeni eklenen requirement analysis metodu
  async runRequirementAnalysis(files, model = null, customPrompt = null, sessionId = null) {
    const formData = new FormData();
    files.forEach(file => {
      const actualFile = file.file || file;
      formData.append('files', actualFile);
    });
    // Dosya tiplerini ayrı bir array olarak ekle
    const types = files.map(fileInfo => fileInfo.type || '');
    types.forEach(type => formData.append('types', type));
    if (model) {
      formData.append('model', model);
    }
    if (customPrompt) {
      formData.append('custom_prompt', customPrompt);
    }
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
  
    try {
      console.log("İstek gönderiliyor: Gereksinim analizi süreci için");
      const response = await axios.post(
        `${API_BASE_URL}/requirement_analysis/run`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      console.log("İstek başarıyla gönderildi: Gereksinim analizi süreci");
      return response.data;
    } catch (error) {
      console.error("Hata detayları:", error.response?.data);
      const errorMsg = error.response?.data?.detail || 'Requirement analysis failed';
      throw new Error(errorMsg);
    }
  },

  async runTestScenarioGeneration(config) {
    try {
        const response = await axios.post(
            `/api/processes/test-scenario-generation/run`, // Use absolute path with /api prefix
            config,
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to generate test scenarios');
    }
  },

  async generatePrompt(formData) {
    try {
        const response = await axios.post(
            `${API_BASE_URL}/processes/test-scenario-generation/generate-prompt`,
            formData,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
        
        if (response.data.status === 'success') {
            return response.data;
        } else {
            throw new Error(response.data.message || 'Failed to generate prompt');
        }
    } catch (error) {
        console.error('Error in generatePrompt:', error);
        throw error;
    }
  },

  async getTestTypeDetails(testType) {
    try {
      console.log('Fetching test type details for:', testType);
      const response = await axios.get(
        `${API_BASE_URL}/test-scenario-generation/test-type/${encodeURIComponent(testType)}`,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      console.log('Received test type details:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching test type details:', error);
      if (error.response?.status === 404) {
        return {
          scoring_elements: {},
          instruction_elements: {}
        };
      }
      throw new Error(error.response?.data?.detail || 'Failed to fetch test type details');
    }
  },

  async runTestPlanning(files, model = null, customPrompt = null, sessionId = null) {
    const formData = new FormData();
    files.forEach(fileInfo => {
      const file = fileInfo.file || fileInfo;
      formData.append('files', file);
    });
    if (model) formData.append('model', model);
    if (customPrompt) formData.append('custom_prompt', customPrompt);
    if (sessionId) formData.append('session_id', sessionId);

    try {
      const response = await fetch('http://localhost:8000/api/processes/test-planning/run', {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error(`Backend error: ${response.status}`);
      const data = await response.json();
      return {
        plans: data.plans.map(plan => `## Files Analyzed\n${plan.files}\n\n## Test Plan\n${plan.plan}`),
        metadata: {
          timestamp: new Date().toISOString(),
          fileCount: files.length
        }
      };
    } catch (error) {
      throw error;
    }
  },

  async runEnvironmentSetup(files, model = null, customPrompt = null, sessionId = null) {
    console.log("runEnvironmentSetup çağrıldı. Dosyalar ve tipleri:");
    files.forEach((fileInfo, idx) => {
      const file = fileInfo.file || fileInfo;
      const type = fileInfo.type || '';
      console.log(`  [${idx}] Dosya adı: ${file.name || file.file?.name}, Tip: \"${type}\"`);
    });

    const formData = new FormData();
    files.forEach(fileInfo => {
      const file = fileInfo.file || fileInfo;
      formData.append('files', file);
    });
    // Dosya tiplerini ayrı bir array olarak ekle
    const types = files.map(fileInfo => fileInfo.type || '');
    console.log("Gönderilecek types array'i:", types);
    types.forEach(type => formData.append('types', type));
    if (model) formData.append('model', model);
    if (customPrompt) formData.append('custom_prompt', customPrompt);
    if (sessionId) formData.append('session_id', sessionId);

    try {
      const response = await fetch('http://localhost:8000/api/processes/environment-setup/run', {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error(`Backend error: ${response.status}`);
      const data = await response.json();
      return {
        setups: data.setups.map(setup => `## Files Analyzed\n${setup.files}\n\n## Environment Setup\n${setup.setup}`),
        metadata: {
          timestamp: new Date().toISOString(),
          fileCount: files.length
        }
      };
    } catch (error) {
      throw error;
    }
  }
};

export default processService;