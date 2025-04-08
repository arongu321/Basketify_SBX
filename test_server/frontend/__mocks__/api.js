// frontend/__mocks__/api.js
const mockApi = {
  create: jest.fn(() => mockApi), // Mocking axios.create
  interceptors: {
    request: {
      use: jest.fn(), // Mocking interceptors
    },
  },
  get: jest.fn(), // Mocking the get method
  post: jest.fn(), // Mocking the post method
  put: jest.fn(), // Mocking the put method
  delete: jest.fn(), // Mocking the delete method
};

export default mockApi;
