
const { GoogleGenerativeAI } = require('@google/generative-ai');

class AIService {
  constructor() {
    this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-pro" });
  }

  async generateDAMAAdvice(userInput) {
    const prompt = `Given the following information about a DAMA applicant, provide specific advice:
    ${userInput}`;
    
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('AI Service Error:', error);
      return 'Unable to generate advice at this moment.';
    }
  }

  async analyzeCandidateProfile(profile) {
    const prompt = `Analyze this candidate profile for DAMA eligibility:
    ${JSON.stringify(profile)}`;
    
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('AI Service Error:', error);
      return 'Unable to analyze profile at this moment.';
    }
  }
}

module.exports = new AIService();
