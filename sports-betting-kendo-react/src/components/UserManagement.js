
import React, { useState } from 'react';
import { TreeList, TreeListColumn } from '@progress/kendo-react-treelist';
import { Dialog, DialogActionsBar } from '@progress/kendo-react-dialogs';
import { Button } from '@progress/kendo-react-buttons';
import { Form, Field, FormElement } from '@progress/kendo-react-form';
import { Input } from '@progress/kendo-react-inputs';
import { DropDownList } from '@progress/kendo-react-dropdowns';

const UserManagement = () => {
    const [users] = useState([
        {
            id: 1,
            username: 'admin',
            email: 'admin@sportsbetting.com',
            role: 'Administrator',
            status: 'Active',
            lastLogin: '2024-01-10T10:30:00',
            subscriptionTier: 'Enterprise',
            totalBets: 450,
            winRate: 68.5,
            parentId: null
        },
        {
            id: 2,
            username: 'john_doe',
            email: 'john@email.com',
            role: 'Premium User',
            status: 'Active',
            lastLogin: '2024-01-10T09:15:00',
            subscriptionTier: 'Premium',
            totalBets: 125,
            winRate: 62.3,
            parentId: 1
        },
        {
            id: 3,
            username: 'jane_smith',
            email: 'jane@email.com',
            role: 'Pro User',
            status: 'Active',
            lastLogin: '2024-01-09T18:45:00',
            subscriptionTier: 'Pro',
            totalBets: 89,
            winRate: 58.7,
            parentId: 1
        },
        {
            id: 4,
            username: 'mike_wilson',
            email: 'mike@email.com',
            role: 'Free User',
            status: 'Inactive',
            lastLogin: '2024-01-08T14:20:00',
            subscriptionTier: 'Free',
            totalBets: 23,
            winRate: 45.2,
            parentId: 1
        }
    ]);

    const [showDialog, setShowDialog] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);

    const handleEdit = (dataItem) => {
        setSelectedUser(dataItem);
        setShowDialog(true);
    };

    const handleClose = () => {
        setShowDialog(false);
        setSelectedUser(null);
    };

    const handleSubmit = (dataItem) => {
        console.log('Updating user:', dataItem);
        setShowDialog(false);
        setSelectedUser(null);
    };

    const ActionCell = (props) => (
        <td>
            <Button 
                size="small" 
                themeColor="primary"
                onClick={() => handleEdit(props.dataItem)}
            >
                Edit
            </Button>
            <Button 
                size="small" 
                themeColor="error"
                style={{ marginLeft: '8px' }}
            >
                Block
            </Button>
        </td>
    );

    const StatusCell = (props) => (
        <td>
            <span className={`status-badge status-${props.dataItem.status.toLowerCase()}`}>
                {props.dataItem.status}
            </span>
        </td>
    );

    const WinRateCell = (props) => (
        <td>
            <div className="win-rate-cell">
                <div className="win-rate-bar">
                    <div 
                        className="win-rate-fill" 
                        style={{ width: `${props.dataItem.winRate}%` }}
                    ></div>
                </div>
                <span>{props.dataItem.winRate.toFixed(1)}%</span>
            </div>
        </td>
    );

    return (
        <div className="user-management-container">
            <div className="user-management-header">
                <h2>User Management</h2>
                <Button themeColor="primary">Add New User</Button>
            </div>

            <TreeList 
                data={users}
                idField="id"
                parentIdField="parentId"
                expandField="expanded"
                height="600px"
            >
                <TreeListColumn field="username" title="Username" width="150px" />
                <TreeListColumn field="email" title="Email" width="200px" />
                <TreeListColumn field="role" title="Role" width="120px" />
                <TreeListColumn field="status" title="Status" width="100px" cell={StatusCell} />
                <TreeListColumn field="subscriptionTier" title="Subscription" width="120px" />
                <TreeListColumn field="totalBets" title="Total Bets" width="100px" />
                <TreeListColumn field="winRate" title="Win Rate" width="120px" cell={WinRateCell} />
                <TreeListColumn field="lastLogin" title="Last Login" width="150px" format="{0:g}" />
                <TreeListColumn title="Actions" width="150px" cell={ActionCell} />
            </TreeList>

            {showDialog && (
                <Dialog title="Edit User" onClose={handleClose} width={500}>
                    <Form
                        initialValues={selectedUser}
                        onSubmit={handleSubmit}
                        render={(formRenderProps) => (
                            <FormElement style={{ maxWidth: 450 }}>
                                <fieldset>
                                    <Field
                                        name="username"
                                        component={Input}
                                        label="Username"
                                    />
                                    <Field
                                        name="email"
                                        component={Input}
                                        label="Email"
                                    />
                                    <Field
                                        name="role"
                                        component={DropDownList}
                                        label="Role"
                                        data={['Administrator', 'Premium User', 'Pro User', 'Free User']}
                                    />
                                    <Field
                                        name="status"
                                        component={DropDownList}
                                        label="Status"
                                        data={['Active', 'Inactive', 'Suspended']}
                                    />
                                </fieldset>
                                <DialogActionsBar>
                                    <Button type="submit" themeColor="primary">
                                        Save Changes
                                    </Button>
                                    <Button onClick={handleClose}>
                                        Cancel
                                    </Button>
                                </DialogActionsBar>
                            </FormElement>
                        )}
                    />
                </Dialog>
            )}
        </div>
    );
};

export default UserManagement;
