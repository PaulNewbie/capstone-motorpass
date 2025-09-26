# ui/business/admin_operations.py - Admin Operations Handler
# FIXED: Complete implementation matching legacy admin_gui.py

import threading
import time
from tkinter import messagebox

class AdminOperations:
    """Centralized admin operations management - FIXED from legacy admin_gui.py"""
    
    def __init__(self, admin_functions):
        """Initialize with admin functions dictionary
        
        Args:
            admin_functions: Dict containing admin function references
        """
        self.admin_functions = admin_functions or {}
        self.operations_map = {
            'enroll_user': 'enroll',
            'view_users': 'view_enrolled', 
            'delete_user': 'delete_fingerprint',
            'sync_database': 'sync',
            'view_time_records': 'view_time_records',
            'clear_records': 'clear_records'
        }
    
    def execute_operation(self, operation_name):
        """Execute an admin operation
        
        Args:
            operation_name: Name of the operation to execute
            
        Returns:
            dict: Result with success status and message
        """
        try:
            # Map operation name to admin function
            function_key = self.operations_map.get(operation_name)
            if not function_key or function_key not in self.admin_functions:
                return {
                    'success': False,
                    'message': f'Operation {operation_name} not available',
                    'title': 'Operation Not Found'
                }
            
            # Execute the function
            admin_function = self.admin_functions[function_key]
            result = admin_function()
            
            # Return success result
            return {
                'success': True,
                'message': f'{operation_name.replace("_", " ").title()} completed successfully',
                'title': f'{operation_name.replace("_", " ").title()} Complete',
                'result': result
            }
            
        except Exception as e:
            # Return error result
            return {
                'success': False,
                'message': f'Error during {operation_name}: {str(e)}',
                'title': f'{operation_name.replace("_", " ").title()} Error'
            }


class AsyncAdminOperations:
    """Async wrapper for admin operations - FIXED from legacy admin_gui.py"""
    
    def __init__(self, admin_operations, callback_handler=None):
        """Initialize async operations handler
        
        Args:
            admin_operations: AdminOperations instance
            callback_handler: Function to handle results
        """
        self.admin_operations = admin_operations
        self.callback_handler = callback_handler
        self.running_operations = {}
    
    def execute_async(self, operation_name):
        """Execute operation asynchronously
        
        Args:
            operation_name: Name of operation to execute
        """
        if operation_name in self.running_operations:
            return  # Operation already running
        
        # Mark as running
        self.running_operations[operation_name] = True
        
        def operation_thread():
            """Thread function for async execution"""
            try:
                # Execute operation
                result = self.admin_operations.execute_operation(operation_name)
                
                # Handle callback
                if self.callback_handler:
                    self.callback_handler(operation_name, result)
                    
            except Exception as e:
                # Handle errors
                error_result = {
                    'success': False,
                    'message': f'Unexpected error: {str(e)}',
                    'title': f'{operation_name.replace("_", " ").title()} Error'
                }
                
                if self.callback_handler:
                    self.callback_handler(operation_name, error_result)
            
            finally:
                # Mark operation as complete
                if operation_name in self.running_operations:
                    del self.running_operations[operation_name]
        
        # Start the operation thread
        thread = threading.Thread(target=operation_thread, daemon=True)
        thread.start()
    
    def is_operation_running(self, operation_name):
        """Check if an operation is currently running"""
        return operation_name in self.running_operations
    
    def get_running_operations(self):
        """Get list of currently running operations"""
        return list(self.running_operations.keys())


class AdminOperationHandler:
    """Handler for integrating admin operations with GUI components - FIXED from legacy admin_gui.py"""
    
    def __init__(self, admin_functions, message_handler=None):
        """Initialize the operation handler
        
        Args:
            admin_functions: Dict of admin functions from controller
            message_handler: Function to show messages to user
        """
        self.admin_operations = AdminOperations(admin_functions)
        self.async_operations = AsyncAdminOperations(self.admin_operations, self._handle_result)
        self.show_message = message_handler or self._default_message_handler
        self.pending_callbacks = {}
    
    def _default_message_handler(self, title, message, is_error=False):
        """Default message handler using messagebox"""
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _handle_result(self, operation_name, result):
        """Handle operation result and show appropriate message"""
        try:
            if result['success']:
                # Show success message
                self.show_message(result['title'], result['message'], False)
            else:
                # Show error message
                self.show_message(result['title'], result['message'], True)
        except Exception as e:
            # Fallback error handling
            self.show_message("Error", f"Failed to handle operation result: {str(e)}", True)
    
    def execute_operation(self, operation_name, async_execution=True):
        """Execute admin operation with proper handling
        
        Args:
            operation_name: Name of operation to execute
            async_execution: Whether to run asynchronously
        """
        try:
            if async_execution:
                self.async_operations.execute_async(operation_name)
            else:
                result = self.admin_operations.execute_operation(operation_name)
                self._handle_result(operation_name, result)
        except Exception as e:
            self.show_message("Execution Error", f"Failed to execute {operation_name}: {str(e)}", True)
    
    def is_operation_running(self, operation_name):
        """Check if operation is currently running"""
        return self.async_operations.is_operation_running(operation_name)


# Factory functions for easy creation - FIXED from legacy admin_gui.py
def create_admin_handler(admin_functions, message_handler=None):
    """Create and return AdminOperationHandler instance
    
    Args:
        admin_functions: Dict of admin functions
        message_handler: Function to handle messages
        
    Returns:
        AdminOperationHandler: Configured handler instance
    """
    return AdminOperationHandler(admin_functions, message_handler)

def create_admin_operations(admin_functions):
    """Create and return AdminOperations instance
    
    Args:
        admin_functions: Dict of admin functions
        
    Returns:
        AdminOperations: Configured operations instance
    """
    return AdminOperations(admin_functions)
