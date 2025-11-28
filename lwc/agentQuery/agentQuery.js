import { LightningElement, track } from 'lwc';
import runAgentQuery from '@salesforce/apex/AgentQueryController.runAgentQuery';

export default class AgentQuery extends LightningElement {
    @track queryText = '';
    @track output = '';
    @track formattedOutput = '';
    @track error = '';
    @track isLoading = false;

    handleQueryChange(event) {
        this.queryText = event.target.value;
    }

    // FIX: Compute disabled state here (LWC does not allow inline expressions)
    get isRunDisabled() {
        return this.isLoading || !this.queryText || this.queryText.trim().length === 0;
    }

    handleRunQuery() {
        this.isLoading = true;
        this.output = '';
        this.error = '';

        runAgentQuery({ queryText: this.queryText })
            .then((res) => {
                this.output = res.output || '';
                this.formattedOutput = this.output; // <pre> keeps formatting
            })
            .catch((err) => {
                this.error = err.body?.message || 'Unknown error';
            })
            .finally(() => {
                this.isLoading = false;
            });
    }
}
