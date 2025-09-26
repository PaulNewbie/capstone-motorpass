# ui/business/admin_operations.py - Admin Business Logic Operations
# KISS principle: Pure business logic, no GUI code

import threading
from datetime import datetime
from tkinter import messagebox

class AdminOperations:
    """Pure business logic for admin operations - no GUI dependencies"""
    
    def __init__(self, admin_functions):
        """Initialize with admin functions from controller
        
        Args:
            admin_functions: Dict of admin function references from controller
        """
        self.admin_functions = admin_functions
        self.operation_results = {}
    
    def enroll_user(self):
        """Enroll new user operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('enroll', lambda: False)()
            return {
                'success': bool(result),
                'message': 'User enrollment completed successfully!' if result else 'User enrollment failed.',
                'title': '👤 Enrollment Complete' if result else '❌ Enrollment Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Enrollment error: {str(e)}',
                'title': '❌ Enrollment Error'
            }
    
    def view_users(self):
        """Get enrolled users data
        
        Returns:
            dict: Result with user data or error
        """
        try:
            users_data = self.admin_functions.get('view_users', lambda: {})()
            return {
                'success': True,
                'data': users_data,
                'count': len(users_data),
                'message': f'Retrieved {len(users_data)} enrolled users.'
            }
        except Exception as e:
            return {
                'success': False,
                'data': {},
                'count': 0,
                'message': f'Error retrieving users: {str(e)}'
            }
    
    def delete_user(self):
        """Delete user operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('delete_fingerprint', lambda: False)()
            return {
                'success': bool(result),
                'message': 'User deleted successfully!' if result else 'User deletion failed.',
                'title': '🗑️ User Deleted' if result else '❌ Deletion Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Deletion error: {str(e)}',
                'title': '❌ Deletion Error'
            }
    
    def sync_database(self):
        """Sync database operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('sync', lambda: False)()
            return {
                'success': bool(result),
                'message': 'Database synchronized successfully!\nCheck terminal for details.' if result else 'Database synchronization failed.',
                'title': '🔄 Sync Complete' if result else '❌ Sync Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'title': '❌ Sync Error'
            }
    
    def get_time_records(self):
        """Get time records data
        
        Returns:
            dict: Result with time records data or error
        """
        try:
            records = self.admin_functions.get('get_time_records', lambda: [])()
            return {
                'success': True,
                'data': records,
                'count': len(records),
                'message': f'Retrieved {len(records)} time records.'
            }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': f'Error retrieving records: {str(e)}'
            }
    
    def clear_time_records(self):
        """Clear all time records operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('clear_records', lambda: False)()
            return {
                'success': bool(result),
                'message': 'All time records have been cleared successfully.' if result else 'Failed to clear time records.',
                'title': '🧹 Records Cleared' if result else '❌ Clear Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Clear records error: {str(e)}',
                'title': '❌ Clear Error'
            }
    
    def get_system_stats(self):
        """Get system statistics
        
        Returns:
            dict: System statistics data
        """
        try:
            stats = self.admin_functions.get('get_stats', lambda: {})()
            
            # Provide default values if stats are missing
            default_stats = {
                'total_students': 0,
                'total_staff': 0,
                'users_currently_in': 0,
                'total_time_records': 0,
                'last_sync': 'Never'
            }
            
            # Merge with actual stats
            for key in default_stats:
                if key not in stats:
                    stats[key] = default_stats[key]
            
            return {
                'success': True,
                'data': stats,
                'message': 'Statistics retrieved successfully.'
            }
        except Exception as e:
            return {
                'success': False,
                'data': {
                    'total_students': 0,
                    'total_staff': 0,
                    'users_currently_in': 0,
                    'total_time_records': 0,
                    'last_sync': 'Error'
                },
                'message': f'Error retrieving statistics: {str(e)}'
            }
    
    def reset_system(self):
        """Reset system operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('reset', lambda: False)()
            return {
                'success': bool(result),
                'message': 'System reset completed successfully!' if result else 'System reset failed.',
                'title': '🔄 System Reset' if result else '❌ Reset Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Reset error: {str(e)}',
                'title': '❌ Reset Error'
            }
    
    def view_admins(self):
        """Get admin accounts data
        
        Returns:
            dict: Result with admin data or error
        """
        try:
            admins_data = self.admin_functions.get('view_admins', lambda: {})()
            return {
                'success': True,
                'data': admins_data,
                'count': len(admins_data) if isinstance(admins_data, dict) else 0,
                'message': 'Admin accounts retrieved successfully.'
            }
        except Exception as e:
            return {
                'success': False,
                'data': {},
                'count': 0,
                'message': f'Error retrieving admins: {str(e)}'
            }
    
    def enroll_guard_admin(self):
        """Enroll guard admin operation
        
        Returns:
            dict: Result with success status and message
        """
        try:
            result = self.admin_functions.get('enroll_guard', lambda: False)()
            return {
                'success': bool(result),
                'message': 'Guard admin enrolled successfully!' if result else 'Guard admin enrollment failed.',
                'title': '🛡️ Guard Enrolled' if result else '❌ Guard Enrollment Failed'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Guard enrollment error: {str(e)}',
                'title': '❌ Guard Enrollment Error'
            }


class AsyncAdminOperations:
    """Async wrapper for admin operations to prevent GUI freezing"""
    
    def __init__(self, admin_operations, callback_handler=None):
        """Initialize with AdminOperations instance
        
        Args:
            admin_operations: AdminOperations instance
            callback_handler: Function to handle operation results
        """
        self.admin_operations = admin_operations
        self.callback_handler = callback_handler
        self.running_operations = {}
    
    def run_async_operation(self, operation_name, operation_method, *args, **kwargs):
        """Run an admin operation asynchronously
        
        Args:
            operation_name: Name of the operation for tracking
            operation_method: Method to execute
            *args, **kwargs: Arguments for the operation method
        """
        def operation_thread():
            try:
                # Mark operation as running
                self.running_operations[operation_name] = True
                
                # Execute the operation
                result = operation_method(*args, **kwargs)
                
                # Handle the result
                if self.callback_handler:
                    self.callback_handler(operation_name, result)
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'message': f'Operation error: {str(e)}',
                    'title': f'❌ {operation_name.title()} Error'
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
        """Check if an operation is currently running
        
        Args:
            operation_name: Name of the operation to check
            
        Returns:
            bool: True if operation is running
        """
        return operation_name in self.running_operations
    
    def get_running_operations(self):
        """Get list of currently running operations
        
        Returns:
            list: List of running operation names
        """
        return list(self.running_operations.keys())


class AdminOperationHandler:
    """Handler for integrating admin operations with GUI components"""
    
    def __init__(self, admin_functions, show_message_func=None):
        """Initialize the operation handler
        
        Args:
            admin_functions: Dict of admin functions from controller
            show_message_func: Function to show messages to user (e.g., messagebox.showinfo)
        """
        self.admin_operations = AdminOperations(admin_functions)
        self.async_operations = AsyncAdminOperations(self.admin_operations, self._handle_result)
        self.show_message = show_message_func or self._default_message_handler
        self.pending_callbacks = {}
    
    def _default_message_handler(self, title, message, is_error=False):
        """Default message handler using tkinter messagebox
        
        Args:
            title: Message title
            message: Message text
            is_error: Whether this is an error message
        """
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _handle_result(self, operation_name, result):
        """Handle operation result
        
        Args:
            operation_name: Name of the completed operation
            result: Operation result dict
        """
        # Show message to user
        if 'title' in result and 'message' in result:
            self.show_message(result['title'], result['message'], not result['success'])
        
        # Call any pending callbacks
        if operation_name in self.pending_callbacks:
            callback = self.pending_callbacks[operation_name]
            callback(result)
            del self.pending_callbacks[operation_name]
    
    def execute_operation(self, operation_name, callback=None):
        """Execute an admin operation
        
        Args:
            operation_name: Name of operation to execute
            callback: Optional callback for when operation completes
        """
        # Store callback if provided
        if callback:
            self.pending_callbacks[operation_name] = callback
        
        # Get the operation method
        operation_method = getattr(self.admin_operations, operation_name, None)
        
        if not operation_method:
            error_result = {
                'success': False,
                'message': f'Unknown operation: {operation_name}',
                'title': '❌ Operation Error'
            }
            self._handle_result(operation_name, error_result)
            return
        
        # Run the operation asynchronously
        self.async_operations.run_async_operation(operation_name, operation_method)
    
    def is_busy(self, operation_name=None):
        """Check if operations are running
        
        Args:
            operation_name: Specific operation to check, or None for any
            
        Returns:
            bool: True if operations are running
        """
        if operation_name:
            return self.async_operations.is_operation_running(operation_name)
        else:
            return len(self.async_operations.get_running_operations()) > 0
    
    def get_stats_sync(self):
        """Get system statistics synchronously (for UI display)
        
        Returns:
            dict: Statistics data
        """
        result = self.admin_operations.get_system_stats()
        return result.get('data', {})
    
    def get_users_sync(self):
        """Get users data synchronously (for UI display)
        
        Returns:
            dict: Users data
        """
        result = self.admin_operations.view_users()
        return result.get('data', {})


# Utility functions for easy integration
def create_admin_handler(admin_functions, message_handler=None):
    """Factory function to create AdminOperationHandler
    
    Args:
        admin_functions: Dict of admin functions
        message_handler: Optional custom message handler
        
    Returns:
        AdminOperationHandler: Ready-to-use operation handler
    """
    return AdminOperationHandler(admin_functions, message_handler)

def create_simple_operations(admin_functions):
    """Factory function to create simple AdminOperations
    
    Args:
        admin_functions: Dict of admin functions
        
    Returns:
        AdminOperations: Simple operations instance
    """
    return AdminOperations(admin_functions)
