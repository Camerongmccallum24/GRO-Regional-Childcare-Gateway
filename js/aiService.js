
const { OpenAIApi, Configuration } = require('openai');

class AIService {
  constructor() {
    this.openai = new OpenAIApi(
      new Configuration({
        apiKey: process.env.OPENAI_API_KEY
      })
    );
  }

  async generateDAMAAdvice(userInput) {
    const prompt = `Given the following information about a DAMA applicant, provide specific advice:
    ${userInput}`;
    
    try {
      const response = await this.openai.createCompletion({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 500
      });
      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('AI Service Error:', error);
      return 'Unable to generate advice at this moment.';
    }
  }

  async analyzeCandidateProfile(profile) {
    const prompt = `Analyze this candidate profile for DAMA eligibility:
    ${JSON.stringify(profile)}`;
    
    try {
      const response = await this.openai.createCompletion({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 300
      });
      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('AI Service Error:', error);
      return 'Unable to analyze profile at this moment.';
    }
  }
}

module.exports = new AIService();
