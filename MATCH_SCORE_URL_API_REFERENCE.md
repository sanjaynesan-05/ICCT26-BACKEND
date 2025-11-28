# Match Score URL Endpoint - Complete API Reference

## Endpoint Details

### PUT /matches/{match_id}/score-url

**Description:** Update or set the match score URL (link to external scorecard)

**Method:** PUT

**URL Parameters:**
- `match_id` (integer, required): The ID of the match to update

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "match_score_url": "https://example.com/matches/123/scorecard"
}
```

**Request Body Fields:**
| Field | Type | Required | Rules |
|-------|------|----------|-------|
| match_score_url | string | Yes | Must be valid HTTP/HTTPS URL, max 500 chars |

---

## Response Formats

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Match score URL updated successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "live",
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "scheduled_start_time": "2025-11-28T10:00:00",
    "actual_start_time": "2025-11-28T10:15:00",
    "match_end_time": "2025-11-28T13:45:00",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "match_score_url": "https://example.com/matches/123/scorecard",
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T14:35:22.450496"
  }
}
```

### Error Response - Invalid URL (422 Unprocessable Entity)

```json
{
  "detail": [
    {
      "loc": ["body", "match_score_url"],
      "msg": "match_score_url must be a valid HTTP or HTTPS URL",
      "type": "value_error"
    }
  ]
}
```

### Error Response - Match Not Found (404 Not Found)

```json
{
  "detail": "Match not found"
}
```

### Error Response - Server Error (500 Internal Server Error)

```json
{
  "detail": "Error updating match score URL"
}
```

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | URL updated successfully |
| 400 | Bad Request | Invalid request body |
| 404 | Not Found | Match with given ID doesn't exist |
| 422 | Unprocessable Entity | URL validation failed |
| 500 | Internal Server Error | Server error occurred |

---

## URL Validation Rules

✅ **Valid URLs:**
- `https://example.com/match/123`
- `https://cricketlive.com/matches/456/scorecard`
- `http://localhost:3000/match/789`
- `https://api.example.com/v1/matches/100/details?token=abc123`

❌ **Invalid URLs:**
- `not-a-url` (no protocol)
- `ftp://example.com/match` (not HTTP/HTTPS)
- `` (empty string)
- Just a domain without protocol

---

## Code Examples

### cURL
```bash
curl -X PUT "http://your-backend-url/api/schedule/matches/1/score-url" \
  -H "Content-Type: application/json" \
  -d '{
    "match_score_url": "https://cricketlive.example.com/match/123/scorecard"
  }'
```

### JavaScript/Fetch API
```javascript
async function updateMatchScoreUrl(matchId, scoreUrl) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}/score-url`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        match_score_url: scoreUrl
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      console.log('URL updated:', result.data.match_score_url);
      return result.data;
    } else {
      console.error('Update failed:', result.message);
    }
  } catch (error) {
    console.error('Error updating match score URL:', error);
  }
}

// Usage
updateMatchScoreUrl(1, "https://example.com/matches/123/scorecard");
```

### Python/Requests
```python
import requests
import json

def update_match_score_url(match_id, score_url):
    """Update match score URL"""
    url = f"http://your-backend-url/api/schedule/matches/{match_id}/score-url"
    
    payload = {
        "match_score_url": score_url
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            print(f"✅ URL Updated: {result['data']['match_score_url']}")
            return result['data']
        else:
            print(f"❌ Error: {result.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

# Usage
update_match_score_url(1, "https://example.com/matches/123/scorecard")
```

### React Component
```jsx
import React, { useState } from 'react';

function UpdateMatchScoreUrl({ matchId }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`/api/schedule/matches/${matchId}/score-url`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_score_url: url })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMessage('✅ URL updated successfully!');
        setUrl('');
      } else {
        setMessage('❌ Failed to update URL');
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleUpdate}>
      <input
        type="text"
        placeholder="Enter match score URL (https://...)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Update URL'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}

export default UpdateMatchScoreUrl;
```

---

## Integration Workflow

### Step 1: Get Match Data
```javascript
const response = await fetch(`/api/schedule/matches/${matchId}`);
const match = await response.json();
console.log(match.data.match_score_url); // null if not set
```

### Step 2: Update Match Score URL
```javascript
const urlUpdateResponse = await fetch(`/api/schedule/matches/${matchId}/score-url`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ match_score_url: 'https://example.com/...' })
});
```

### Step 3: Display in UI
```javascript
const updatedMatch = await urlUpdateResponse.json();
if (updatedMatch.data.match_score_url) {
  // Display clickable link to scorecard
  console.log(`Scorecard: ${updatedMatch.data.match_score_url}`);
}
```

---

## Best Practices

1. **Always validate URL format client-side before sending**
   ```javascript
   function isValidUrl(string) {
     try {
       new URL(string);
       return true;
     } catch (_) {
       return false;
     }
   }
   ```

2. **Handle errors gracefully**
   ```javascript
   if (response.status === 422) {
     // URL validation failed
     console.log('Invalid URL format');
   } else if (response.status === 404) {
     // Match not found
     console.log('Match not found');
   }
   ```

3. **Show user feedback on success/failure**
   ```javascript
   if (result.success) {
     showSuccessNotification('Match score URL updated!');
   } else {
     showErrorNotification('Failed to update URL');
   }
   ```

4. **Allow users to clear URL** (set to empty string endpoint if needed)
   - Currently, the endpoint requires a valid URL
   - To clear, you may need separate endpoint or allow null in request

---

## Related Endpoints

Get the updated match with all details including match_score_url:
```
GET /api/schedule/matches/{match_id}
```

Get all matches (includes match_score_url field for each):
```
GET /api/schedule/matches
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 422 Validation Error | Ensure URL starts with `http://` or `https://` |
| 404 Not Found | Verify match_id is correct and match exists |
| 500 Server Error | Check server logs, may be database issue |
| URL not persisting | Ensure response shows updated match_score_url |

---

## Changelog

**Version 1.0** - November 28, 2025
- Initial release of match_score_url endpoint
- URL validation implemented
- Database migration applied
- Full API documentation provided
