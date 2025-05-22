
const aiService = require('./js/aiService');

document.addEventListener('DOMContentLoaded', () => {
  // AI-powered advice generation
  const adviceForm = document.getElementById('adviceForm');
  const adviceOutput = document.getElementById('adviceOutput');

  adviceForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userInput = document.getElementById('userInput').value;
    adviceOutput.textContent = 'Generating advice...';
    
    try {
      const advice = await aiService.generateDAMAAdvice(userInput);
      adviceOutput.textContent = advice;
    } catch (error) {
      adviceOutput.textContent = 'Error generating advice. Please try again.';
    }
  });

  // Profile analysis
  const profileForm = document.getElementById('profileForm');
  const analysisOutput = document.getElementById('analysisOutput');

  profileForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const profile = {
      role: document.getElementById('role').value,
      experience: document.getElementById('experience').value,
      region: document.getElementById('region').value,
      qualifications: document.getElementById('qualifications').value
    };
    
    analysisOutput.textContent = 'Analyzing profile...';
    
    try {
      const analysis = await aiService.analyzeCandidateProfile(profile);
      analysisOutput.textContent = analysis;
    } catch (error) {
      analysisOutput.textContent = 'Error analyzing profile. Please try again.';
    }
  });
});
