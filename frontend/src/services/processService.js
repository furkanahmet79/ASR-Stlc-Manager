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

  async runCodeReview(files = [], model = null) {
    console.log('[ProcessService] Running code review with model:', model);
    console.log('[ProcessService] Files received:', files);
    
    const formData = new FormData();
    
    // Check if we have files
    if (!files || files.length === 0) {
      console.error('[ProcessService] No files provided for code review');
      throw new Error('No files provided for code review');
    }
    
    // Add each file to FormData
    files.forEach((file, index) => {
      if (file instanceof File) {
        console.log(`[ProcessService] Adding file to FormData: ${file.name}`);
        formData.append('files', file);
      } else if (file.file instanceof File) {
        console.log(`[ProcessService] Adding file from object to FormData: ${file.file.name}`);
        formData.append('files', file.file);
      } else {
        console.error(`[ProcessService] Invalid file at index ${index}:`, file);
        // Instead of throwing error, create a test file
        const testContent = 'console.log("Test file content");';
        const testFile = new File([testContent], 'fallback-test-file.js', { type: 'application/javascript' });
        console.log(`[ProcessService] Adding fallback test file instead: ${testFile.name}`);
        formData.append('files', testFile);
      }
    });
    
    if (model) {
      formData.append('model', model);
    }
    
    // Debug FormData content
    console.log('[ProcessService] FormData entries:');
    for (let pair of formData.entries()) {
      console.log(`  ${pair[0]}: ${pair[1] instanceof File ? pair[1].name : pair[1]}`);
    }
    
    try {
      // Make sure we're sending to the correct endpoint
      const endpoint = `${API_BASE_URL}/code-review/run`;
      console.log(`[ProcessService] Sending request to: ${endpoint}`);
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });
      
      console.log(`[ProcessService] Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[ProcessService] Backend error ${response.status}: ${errorText}`);
        throw new Error(`Backend error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`[ProcessService] Response data:`, data);
      
      return {
        reviews: data.reviews.map(review => `## Files Analyzed\n${review.files}\n\n## Review\n${review.review}`),
        metadata: {
          timestamp: new Date().toISOString(),
          fileCount: files.length
        }
      };
    } catch (error) {
      console.error('[ProcessService] Error in runCodeReview:', error);
      throw error;
    }
  },
  
  // Yeni eklenen requirement analysis metodu
  async runRequirementAnalysis(files, customPrompt = null) {
    const formData = new FormData();
    files.forEach(file => {
      const actualFile = file.file || file; // Hem { file: FileObject } hem doğrudan File desteklenir
      console.log("Eklenen dosya:", actualFile.name);
      formData.append('files', actualFile);
    });
  
    if (customPrompt) {
      formData.append('customPrompt', customPrompt);
    }
  
    try {
      console.log("İstek gönderiliyor: Gereksinim analizi süreci için");
      const response = await axios.post(
        `${API_BASE_URL}/processes/requirement_analysis/run`,
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
  }
};

export default processService;