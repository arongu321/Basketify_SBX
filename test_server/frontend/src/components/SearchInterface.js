import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import { ACCESS_TOKEN } from "../utils/constants";
import "./SearchInterface.css";

function SearchInterface() {
  const [message, setMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchPerformed, setSearchPerformed] = useState(false); // flag to tell if user has searched (used to display "no results" only after search)
  const [loading, setLoading] = useState(false); // track if search is done yet (since request is asynchronous)
  const navigate = useNavigate();
  const location = useLocation();

  const accessToken = localStorage.getItem(ACCESS_TOKEN);
  const setFavorite = location.state?.setFavorite; // 'player' or 'team'
  const [searchType, setSearchType] = useState(setFavorite || "player"); // default to 'player' if no state is passed

  const handleSearch = () => {
    setSearchPerformed(true);
    setLoading(true);
    const url =
      searchType === "player"
        ? "http://localhost:8000/api/search-player"
        : "http://localhost:8000/api/search-team";

    axios
      .get(url, { params: { name: searchTerm } })
      .then((response) => {
        if (searchType === "player") {
          setSearchResults(response.data.players);
        } else {
          setSearchResults(response.data.teams);
        }
        setLoading(false); // done loading
      })
      .catch((error) => {
        setLoading(false);
        console.error("Error fetching search results:", error);
      });
  };

  const handleClick = (name) => {
    if (setFavorite) {
      axios
        .post(
          "http://localhost:8000/accounts/set-favorite/",
          {
            type: setFavorite,
            name: name,
          },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`, // django checks if user logged in so pass token
            },
          }
        )
        .then(() => {
          navigate("/"); // return to dashboard after saving
        })
        .catch((error) => {
          console.error("Error saving favorite:", error);
        });
    } else {
      navigate(`/stats/${searchType}/${name}`);
    }
  };

  return (
    <div className="search-interface-container">
      <div className="search-interface-top-banner">
        <button className="back-button" onClick={() => navigate(-1)}>
          Back
        </button>
        <div className="search-interface-header-content">
          <h1 className="search-interface-title">
            Search {searchType.charAt(0).toUpperCase() + searchType.slice(1)}s
          </h1>
        </div>
      </div>

      <div className="search-interface-content">
        {/* Conditional rendering of search type buttons */}
        {!setFavorite && (
          <div className="search-interface-type-buttons">
            <button
              className={searchType === "player" ? "active" : ""}
              onClick={() => setSearchType("player")}
            >
              Search Players
            </button>
            <button
              className={searchType === "team" ? "active" : ""}
              onClick={() => setSearchType("team")}
            >
              Search Teams
            </button>
          </div>
        )}

        {/* Search Input */}
        <div className="search-interface-bar">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={`Enter ${searchType} name`}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSearch();
            }}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        {/* Display Search Results */}
        {searchResults.length > 0 && (
          <div className="search-interface-results">
            <h3>Search Results:</h3>
            <ul>
              {searchResults.map((result, index) => (
                <li
                  key={index}
                  onClick={() => handleClick(result.name)}
                  className="search-interface-result-item"
                >
                  {result.name}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* No results message */}
        {searchPerformed && !loading && searchResults.length === 0 && (
          <div className="search-interface-no-results">
            <h3>No results found for "{searchTerm}".</h3>
          </div>
        )}
      </div>

      <div className="search-interface-bottom-banner"></div>
    </div>
  );
}

export default SearchInterface;
