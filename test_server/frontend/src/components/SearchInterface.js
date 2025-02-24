import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Use useNavigate instead of useHistory

function SearchInterface() {
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchType, setSearchType] = useState('player'); // 'player' or 'team'
  const [searchResults, setSearchResults] = useState([]);
  const navigate = useNavigate(); // useNavigate hook to navigate to a new page

  // Fetch the search message from the backend
  useEffect(() => {
    axios.get('http://localhost:8000/api/search-message/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error("There was an error fetching the search interface message:", error);
      });
  }, []);

  // Function to handle the search
  const handleSearch = () => {
    const url = `http://localhost:8000/api/search-${searchType}`;
    axios.get(url, { params: { name: searchTerm } })
      .then(response => {
        setSearchResults(response.data.results);  // Assume response contains 'results'
      })
      .catch(error => {
        console.error("Error fetching search results:", error);
      });
  };

  // Handle clicking on a player's or team's name
  const handleClick = (name) => {
    // Navigate to the player's or team's stats page
    navigate(`/stats/${searchType}/${name}`);
  };

  return (
    <div>
      <h1>Search Interface Page</h1>
      <p>{message}</p>

      <div>
        <button onClick={() => setSearchType('player')}>Search Players</button>
        <button onClick={() => setSearchType('team')}>Search Teams</button>
      </div>

      <div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={`Enter ${searchType} name`}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {searchResults.length > 0 && (
        <div>
          <h3>Search Results:</h3>
          <ul>
            {searchResults.map((result, index) => (
              <li key={index} onClick={() => handleClick(result.name)}>
                {result.name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SearchInterface;
