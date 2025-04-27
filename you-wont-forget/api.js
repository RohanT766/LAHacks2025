// api.js
const API_BASE_URL = 'http://localhost:8000'; // Update for production

/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User's email
 * @param {string} userData.password - User's password
 * @param {string} userData.nickname - User's nickname
 * @param {string} userData.phone - User's phone number (optional)
 * @returns {Promise<Object>} Registration response
 */
export const registerUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      // Create a custom error with additional properties
      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    // Add retry logic here if needed
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Login a user
 * @param {Object} credentials - User login credentials
 * @param {string} credentials.email - User's email
 * @param {string} credentials.password - User's password
 * @returns {Promise<Object>} Login response
 */
export const loginUser = async (credentials) => {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(credentials)
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Create a new task
 * @param {Object} taskData - Task data
 * @param {string} taskData.user_id - User's ID
 * @param {string} taskData.description - Task description
 * @param {string} taskData.frequency - Task frequency
 * @param {string} taskData.charity_id - Charity ID
 * @param {number} taskData.donation_amount - Donation amount in cents
 * @param {string} taskData.due_date - Due date in ISO format
 * @returns {Promise<Object>} Task creation response
 */
export const createTask = async (taskData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/task`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(taskData)
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Fetch all charities
 * @returns {Promise<Array>} List of charities
 */
export const getCharities = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/charities`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Fetch tasks for a user
 * @param {string} userId - User's ID
 * @returns {Promise<Array>} List of tasks
 */
export const getUserTasks = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/${userId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Update user's Twitter credentials
 * @param {Object} data - Twitter update data
 * @param {string} data.user_id - User's ID
 * @param {Object} data.twitter - Twitter credentials object
 * @returns {Promise<Object>} Update response
 */
export const updateTwitter = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/update-twitter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      let errorMessage;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (parseError) {
          errorMessage = `Error ${response.status}: Could not parse error response`;
        }
      } else {
        try {
          errorMessage = await response.text();
        } catch (textError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.statusText = response.statusText;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};