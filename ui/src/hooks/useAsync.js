import { useState, useCallback, useEffect } from 'react';

/**
 * Custom hook for managing async API calls with loading and error states
 * @param {Function} apiCall - The async API function to call
 * @param {*} initialData - Initial data state
 * @param {boolean} autoExecute - Whether to execute the API call on mount (default: false)
 * @returns {Object} - { data, loading, error, execute, setData, setError }
 */
export const useAsync = (apiCall, initialData = null, autoExecute = false) => {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall(...args);
      if (result.success) {
        setData(result.data);
        return result.data;
      } else {
        throw new Error(result.error);
      }
    } catch (err) {
      const errorMessage = err.message || 'An error occurred';
      setError(errorMessage);
      console.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Auto-execute on mount if requested
  useEffect(() => {
    if (autoExecute) {
      execute();
    }
  }, [autoExecute, execute]);

  return { data, loading, error, execute, setData, setError };
};

/**
 * Custom hook for managing form state and validation
 * @param {Object} initialValues - Initial form values
 * @param {Function} onSubmit - Callback when form is submitted
 * @returns {Object} - { values, handleChange, handleSubmit, reset, errors, setErrors }
 */
export const useForm = (initialValues, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  }, []);

  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  }, []);

  const handleSubmit = useCallback(async (e) => {
    if (e?.preventDefault) e.preventDefault();
    
    try {
      await onSubmit(values);
    } catch (err) {
      // Errors are handled by the onSubmit function
    }
  }, [values, onSubmit]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return {
    values,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    errors,
    setErrors,
    touched,
    setValues
  };
};

/**
 * Custom hook for managing pagination
 * @param {number} itemsPerPage - Number of items per page
 * @returns {Object} - { currentPage, totalPages, paginate, goToPage, reset }
 */
export const usePagination = (itemsPerPage = 10) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginate = useCallback((items) => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return items.slice(startIndex, endIndex);
  }, [currentPage, itemsPerPage]);

  const getTotalPages = useCallback((totalItems) => {
    return Math.ceil(totalItems / itemsPerPage);
  }, [itemsPerPage]);

  const goToPage = useCallback((pageNumber) => {
    setCurrentPage(Math.max(1, pageNumber));
  }, []);

  const reset = useCallback(() => {
    setCurrentPage(1);
  }, []);

  return {
    currentPage,
    paginate,
    getTotalPages,
    goToPage,
    reset,
    itemsPerPage
  };
};

/**
 * Custom hook for managing filters
 * @param {Object} initialFilters - Initial filter values
 * @returns {Object} - { filters, setFilter, clearFilter, clearAllFilters }
 */
export const useFilters = (initialFilters = {}) => {
  const [filters, setFilters] = useState(initialFilters);

  const setFilter = useCallback((key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const clearFilter = useCallback((key) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[key];
      return newFilters;
    });
  }, []);

  const clearAllFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  return {
    filters,
    setFilter,
    clearFilter,
    clearAllFilters,
    hasFilters: Object.keys(filters).length > 0
  };
};
