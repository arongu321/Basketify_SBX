import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

function SearchInterface() {
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchType, setSearchType] = useState('player');
  const [searchResults, setSearchResults] = useState([]);
  const navigate = useNavigate();
  const location = useLocation(); // Get state passed from navigation


  useEffect(() => {
    axios.get('http://localhost:8000/api/search-message/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error("There was an error fetching the search interface message:", error);
      });
  }, []);


  const handleSearch = () => {
    const url = searchType === 'player'
      ? 'http://localhost:8000/api/search-player'
      : 'http://localhost:8000/api/search-team';

    axios.get(url, { params: { name: searchTerm } })
      .then(response => {
        if (searchType === 'player') {
          setSearchResults(response.data.players);
        } else {
          setSearchResults(response.data.teams);
        }
      })
      .catch(error => {
        console.error("Error fetching search results:", error);
      });
  };


  const handleClick = (name) => {
    const setFavorite = location.state?.setFavorite;  // check if call is for setting a favorite
    if (setFavorite) {
      // save fave to the backend
      axios.post('http://localhost:8000/api/set-favorite/', {
        type: setFavorite,
        name: name
      })
        .then(() => {
          navigate('/'); // return to dashboard after saving
        })
        .catch(error => {
          console.error("Error saving favorite:", error);
        });
    } else {
      // normal navigation to stats page (want to see player/team stats)
      navigate(`/stats/${searchType}/${name}`);
    }
  };

  return (
    <div>
      <h1>Search Interface Page</h1>
      <p>{message}</p>

      <div>
        <button onClick={() => { 
          setSearchType('player'); 
          setSearchResults([]); // Clear results when switching to player search
        }}>
          Search Players
        </button>
        <button onClick={() => { 
          setSearchType('team'); 
          setSearchResults([]); // Clear results when switching to team search
        }}>
          Search Teams
        </button>
      </div>

      <div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={`Enter ${searchType} name`}
          onKeyDown={(e) => {  // perform search on 'Enter' key
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {searchResults.length > 0 && (
        <div>
          <h3>Search Results:</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                {searchType === 'player' && <th>Position</th>}
                {searchType === 'player' && <th>Team</th>}
                {searchType === 'team' && <th>Location</th>}
              </tr>
            </thead>
            <tbody>
              {searchResults.map((result, index) => (
                <tr key={index} onClick={() => handleClick(result.name)}>
                  <td 
                    style={{
                      color: 'blue', 
                      textDecoration: 'underline', 
                      cursor: 'pointer'
                    }}
                  >
                    {result.name}
                  </td>
                  {searchType === 'player' && <td>{result.position}</td>}
                  {searchType === 'player' && <td>{result.team}</td>}
                  {searchType === 'team' && <td>{result.location}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default SearchInterface;
