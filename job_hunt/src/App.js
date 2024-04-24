import React, { useState } from 'react';
import Papa from 'papaparse';
import { TextField, Button, Box, CircularProgress, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { saveAs } from 'file-saver';


function App() {
  const [jobName, setJobName] = useState('');
  const [countryName, setCountryName] = useState('');
  const [timeRange, setTimeRange] = useState('f_TPR=r604800');

  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [csvContent, setCsvContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDownloadCSV = () => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    saveAs(blob, 'downloaded_data.csv');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      // const scrapeResponse = await fetch(`https://job-hunt-j0m6.onrender.com/scrape`, {
      const scrapeResponse = await fetch(`http://localhost:5000/scrape`, {

        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_name: jobName, country_name: countryName, time_range: timeRange }),
      });
      if (!scrapeResponse.ok) {
        throw new Error(`HTTP error! status: ${scrapeResponse.status}`);
      }
      const { filename } = await scrapeResponse.json();
      
      // const csvResponse = await fetch(`https://job-hunt-j0m6.onrender.com/download/${filename}`);
      const csvResponse = await fetch(`http://localhost:5000/download/${filename}`);

      if (!csvResponse.ok) {
        throw new Error(`HTTP error! status: ${csvResponse.status}`);
      }
      const text = await csvResponse.text();
      setCsvContent(text);
      Papa.parse(text, {
        header: true,
        skipEmptyLines: true,
        complete: (result) => {
          if (result.meta.fields) {
            const newColumns = result.meta.fields.map((field) => ({
              field: field,
              headerName: field,
              width: 150, // adjust width as needed
            }));
            setColumns(newColumns);
            setTableData(result.data.map((row, index) => ({ id: index + 1, ...row })));
          } else {
            console.error("No fields found in CSV data");
          }
          setLoading(false);
        },
      });
    } catch (error) {
      console.error("There was an error with the fetch operation:", error.message);
      setLoading(false);
    }
  };

  return (
       <Box style={{ maxWidth: '100%', marginTop: '20px', padding: '20px' }}>
      <Typography variant="h4" gutterBottom>Job Hunt</Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <TextField
          label="Job Name"
          variant="outlined"
          value={jobName}
          onChange={(e) => setJobName(e.target.value)}
          required
        />
        <TextField
          label="Country Name"
          variant="outlined"
          value={countryName}
          onChange={(e) => setCountryName(e.target.value)}
          required
        />
         <FormControl variant="outlined" sx={{ minWidth: 120 }}>
          <InputLabel id="time-range-select-label">Time Range</InputLabel>
          <Select
            labelId="time-range-select-label"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            label="Time Range"
          >
            <MenuItem value="f_TPR=r86400">Past 24 hr</MenuItem>
            <MenuItem value="f_TPR=r604800">Past Week</MenuItem>
          </Select>
          
        </FormControl>
        <Button variant="contained" color="primary" type="submit" disabled={loading}>
          Start Hunting
        </Button>
        <Button variant="contained" color="secondary" onClick={handleDownloadCSV} >
        Download File
      </Button>
      </Box>
      {loading ? (
         <Box display="flex" justifyContent="center">
         <CircularProgress />
         <br></br>
         <Typography variant="h6" style={{ marginTop: '10px' }}>Please keep patience ...... The most effective scraping is often the one that takes time.</Typography>

       </Box>
     ) : (
      <Box style={{ height: '50%', width: '100%' }}>
              <Typography variant="h4" gutterBottom> {jobName}  {countryName}</Typography>

        <DataGrid
          rows={tableData}
          columns={columns}
          pageSize={5}
          rowsPerPageOptions={[5, 10, 20]}
          checkboxSelection
          disableSelectionOnClick
          sx={{
            boxShadow: 2,
            border: 2,
            borderColor: 'primary.light',
            '& .MuiDataGrid-cell:hover': {
              color: 'primary.main',
            },
          }}
        />
      </Box>
        )}
      
    </Box>
  );
}

export default App;
