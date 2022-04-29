pragma solidity ^0.8.12;

contract register {

    address[] _name;
    uint[] _password;
    string[] _email;

    mapping(address => bool) public users;
    mapping(address => bool) public spoc;

    function registerUser(address name,uint password,string memory email) public{

        require(!users[name]);

        users[name]=true;
        _name.push(name);
        _password.push(password);
        _email.push(email);
    }

    function viewUsers() public view returns(address[] memory,uint[] memory,string[] memory) {

        return(_name,_password,_email);
    }

    function loginUser(address name,uint password) public view returns(bool) {

        uint i;
        uint j=0;
        require(users[name]);

        if(_name.length>0) {
            for(i=0;i<_name.length;i++) {
                if(((_name[i])==(name))){
                    j=i;
                }
            }
        }

        if(_password[j]==password && _name[j]==name) {
            return true;
        } else {
            return false;
        }
    }

    function addSpoc(address a) public {

        require(users[a]);
        spoc[a]=true;

    }

    function checkSpoc(address a) public view returns(bool) {
        if(spoc[a]==true)
            return true;
        else
            return false;
    }

}